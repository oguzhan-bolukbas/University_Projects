USE [DATABASE_OF_GATEM]
GO
/****** Object:  Trigger [dbo].[TRIG_TEACHER_DEPARTMENT_UPDATE]    Script Date: 05-Jan-18 16:22:28 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
ALTER TRIGGER [dbo].[TRIG_TEACHER_DEPARTMENT_UPDATE] ON [dbo].[TEACHER_DEPARTMENT]
  FOR UPDATE
  AS
    DECLARE @max INT
    DECLARE @min INT
    DECLARE @prev INT
    DECLARE @idx INT
    DECLARE @time SMALLDATETIME
    SELECT @max=max(_IDX),@min=min(_IDX) FROM inserted
    UPDATE TEACHER_DEPARTMENT_LOG SET _Deleted=1,_UpdateDate=GETDATE()
      WHERE @max=_EndIndex AND @min=_BeginIndex AND _deleted=0
    SET @time=GETDATE()
    UPDATE TEACHER_DEPARTMENT_LOG SET _UpdateDate=@time
      WHERE @max<=_EndIndex AND @min>=_BeginIndex AND _deleted=0
