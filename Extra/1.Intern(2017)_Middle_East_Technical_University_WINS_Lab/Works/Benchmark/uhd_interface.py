#!/usr/bin/python2
#
# Copyright 2010,2011 Free Software Foundation, Inc.
# 
# This file is part of GNU Radio
# 
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

from gnuradio import gr, uhd
from gnuradio import eng_notation
from gnuradio.eng_option import eng_option
from optparse import OptionParser

import sys

def add_freq_option(parser):
    """
    Hackery that has the -f / --freq option set both tx_freq and rx_freq
    """
    def freq_callback(option, opt_str, value, parser):
        parser.values.rx_freq = value
        parser.values.tx_freq = value

    if not parser.has_option('--freq'):
        parser.add_option('-f', '--freq', type="eng_float",
                          action="callback", callback=freq_callback,
                          help="set Tx and/or Rx frequency to FREQ [default=%default]",
                          metavar="FREQ")

class uhd_interface:
    def __init__(self, istx, args, sym_rate, sps, freq=None, lo_offset=None,
                 gain=None, spec=None, antenna=None, clock_source=None):
        
        if(istx):
            self.u = uhd.usrp_sink(device_addr=args, stream_args=uhd.stream_args('fc32'))
        else:
            self.u = uhd.usrp_source(device_addr=args, stream_args=uhd.stream_args('fc32'))

        # Set clock source
        if(clock_source):
            self.u.set_clock_source(clock_source, 0)

        # Set the subdevice spec
        if(spec):
            self.u.set_subdev_spec(spec, 0)

        # Set the antenna
        if(antenna):
            self.u.set_antenna(antenna, 0)
        
        self._args = args
        self._ant  = antenna
        self._spec = spec
        self._gain = self.set_gain(gain)
        self._lo_offset = lo_offset 
        self._freq = self.set_freq(freq, lo_offset) 
        self._rate, self._sps = self.set_sample_rate(sym_rate, sps)
        self._clock_source = clock_source 

    def set_sample_rate(self, sym_rate, req_sps):
        start_sps = req_sps
        while(True):
            asked_samp_rate = sym_rate * req_sps
            self.u.set_samp_rate(asked_samp_rate)
            actual_samp_rate = self.u.get_samp_rate()

            sps = actual_samp_rate/sym_rate
            if(sps < 2):
                req_sps +=1
            else:
                actual_sps = sps
                break
        
        if(sps != req_sps):
            print "\nSymbol Rate:         %f" % (sym_rate)
            print "Requested sps:       %f" % (start_sps)
            print "Given sample rate:   %f" % (actual_samp_rate)
            print "Actual sps for rate: %f" % (actual_sps)

        if(actual_samp_rate != asked_samp_rate):
            print "\nRequested sample rate: %f" % (asked_samp_rate)
            print "Actual sample rate: %f" % (actual_samp_rate)

        return (actual_samp_rate, actual_sps)

    def get_sample_rate(self):
        return self.u.get_samp_rate()
    
    def set_gain(self, gain=None):
        if gain is None:
            # if no gain was specified, use the mid-point in dB
            g = self.u.get_gain_range()
            gain = float(g.start()+g.stop())/2
            print "\nNo gain specified."
            print "Setting gain to %f (from [%f, %f])" % \
                (gain, g.start(), g.stop())
        
        self.u.set_gain(gain, 0)
        return gain

    def set_freq(self, freq=None, lo_offset=None):
        if(freq is None):
            sys.stderr.write("You must specify -f FREQ or --freq FREQ\n")
            sys.exit(1)
        
        r = self.u.set_center_freq(uhd.tune_request(freq, lo_offset))
        if r:
            return freq
        else:
            frange = self.u.get_freq_range()
            sys.stderr.write(("\nRequested frequency (%f) out or range [%f, %f]\n") % \
                                 (freq, frange.start(), frange.stop()))
            sys.exit(1)

#-------------------------------------------------------------------#
#   TRANSMITTER
#-------------------------------------------------------------------#

class uhd_transmitter(uhd_interface, gr.hier_block2):
    def __init__(self, args, sym_rate, sps, freq=None, lo_offset=None, gain=None,
                 spec=None, antenna=None, clock_source=None, verbose=False):
        gr.hier_block2.__init__(self, "uhd_transmitter",
                                gr.io_signature(1,1,gr.sizeof_gr_complex),
                                gr.io_signature(0,0,0))

        # Set up the UHD interface as a transmitter
        uhd_interface.__init__(self, True, args, sym_rate, sps,
                               freq, lo_offset, gain, spec, antenna, clock_source)

        self.connect(self, self.u)

        if(verbose):
            self._print_verbage()

    @staticmethod
    def add_options(parser):
        add_freq_option(parser)
        parser.add_option("-a", "--args", type="string", default="",
                          help="UHD device address args [default=%default]")
        parser.add_option("", "--spec", type="string", default=None,
                          help="Subdevice of UHD device where appropriate")
        parser.add_option("-A", "--antenna", type="string", default=None,
                          help="select Rx Antenna where appropriate")
        parser.add_option("", "--tx-freq", type="eng_float", default=None,
                          help="set transmit frequency to FREQ [default=%default]",
                          metavar="FREQ")
        parser.add_option("", "--lo-offset", type="eng_float", default=0,
                          help="set local oscillator offset in Hz (default is 0)")
        parser.add_option("", "--tx-gain", type="eng_float", default=None,
                          help="set transmit gain in dB (default is midpoint)")
        parser.add_option("-C", "--clock-source", type="string", default=None,
                          help="select clock source (e.g. 'external') [default=%default]") 
        parser.add_option("-v", "--verbose", action="store_true", default=False)

    def _print_verbage(self):
        """
        Prints information about the UHD transmitter
        """
        print "\nUHD Transmitter:"
        print "Args:     %s"    % (self._args)
        print "Freq:        %sHz"  % (eng_notation.num_to_str(self._freq))
        print "LO Offset:    %sHz"  % (eng_notation.num_to_str(self._lo_offset)) 
        print "Gain:        %f dB" % (self._gain)
        print "Sample Rate: %ssps" % (eng_notation.num_to_str(self._rate))
        print "Antenna:     %s"    % (self._ant)
        print "Subdev Spec:  %s"   % (self._spec)
        print "Clock Source: %s"    % (self._clock_source)

#-------------------------------------------------------------------#
#   RECEIVER
#-------------------------------------------------------------------#


class uhd_receiver(uhd_interface, gr.hier_block2):
    def __init__(self, args, sym_rate, sps, freq=None, lo_offset=None, gain=None,
                 spec=None, antenna=None, clock_source=None, verbose=False):
        gr.hier_block2.__init__(self, "uhd_receiver",
                                gr.io_signature(0,0,0),
                                gr.io_signature(1,1,gr.sizeof_gr_complex))
      
        # Set up the UHD interface as a receiver
        uhd_interface.__init__(self, False, args, sym_rate, sps,
                               freq, lo_offset, gain, spec, antenna, clock_source)

        self.connect(self.u, self)

        if(verbose):
            self._print_verbage()

    @staticmethod
    def add_options(parser):
        add_freq_option(parser)
        parser.add_option("-a", "--args", type="string", default="",
                          help="UHD device address args [default=%default]")
        parser.add_option("", "--spec", type="string", default=None,
                          help="Subdevice of UHD device where appropriate")
        parser.add_option("-A", "--antenna", type="string", default=None,
                          help="select Rx Antenna where appropriate")
        parser.add_option("", "--rx-freq", type="eng_float", default=None,
                          help="set receive frequency to FREQ [default=%default]",
                          metavar="FREQ")
        parser.add_option("", "--lo-offset", type="eng_float", default=0,
                          help="set local oscillator offset in Hz (default is 0)") 
        parser.add_option("", "--rx-gain", type="eng_float", default=None,
                          help="set receive gain in dB (default is midpoint)")
        parser.add_option("-C", "--clock-source", type="string", default=None,
                          help="select clock source (e.g. 'external') [default=%default]") 
        if not parser.has_option("--verbose"):
            parser.add_option("-v", "--verbose", action="store_true", default=False)

    def _print_verbage(self):
        """
        Prints information about the UHD transmitter
        """
        print "\nUHD Receiver:"
        print "UHD Args:     %s"    % (self._args)
        print "Freq:         %sHz"  % (eng_notation.num_to_str(self._freq))
        print "LO Offset:    %sHz"  % (eng_notation.num_to_str(self._lo_offset)) 
        print "Gain:         %f dB" % (self._gain)
        print "Sample Rate:  %ssps" % (eng_notation.num_to_str(self._rate))
        print "Antenna:      %s"    % (self._ant)
        print "Spec:         %s"    % (self._spec)
        print "Clock Source: %s"    % (self._clock_source) 

