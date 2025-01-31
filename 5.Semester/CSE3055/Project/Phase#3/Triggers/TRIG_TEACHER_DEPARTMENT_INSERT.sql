USE [DATABASE_OF_GATEM]
GO
/****** Object:  Trigger [dbo].[TRIG_TEACHER_DEPARTMENT_INSERT]    Script Date: 05-Jan-18 16:22:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
ALTER TRIGGER [dbo].[TRIG_TEACHER_DEPARTMENT_INSERT] ON [dbo].[TEACHER_DEPARTMENT]
  FOR INSERT
  AS
    DECLARE @max INT
    DECLARE @min INT
    SELECT @max=max(_IDX),@min=min(_IDX) FROM inserted
    INSERT INTO TEACHER_DEPARTMENT_LOG(_BeginIndex, _EndIndex, _AddingDate, _Deleted)
      VALUES(@min,@max,GETDATE(),0)
