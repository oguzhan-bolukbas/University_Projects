SELECT DISTINCT tcl.ClassCode,l.LessonCode,l.LessonName
FROM TEACHER_CLASS_LESSON tcl
INNER JOIN LESSON l
ON tcl.LessonCode=l.LessonCode AND tcl.ClassCode LIKE '10%'

SELECT l.LessonName,lb.BranchCode,b.BranchName
FROM LESSON l 
FULL OUTER JOIN LESSON_BRANCH lb
ON lb.LessonCode=l.LessonCode
FULL OUTER JOIN BRANCH b
ON lb.BranchCode=b.BranchCode
ORDER BY BranchCode DESC,BranchName DESC

SELECT td.*
FROM TEACHER_DEPARTMENT td,TEACHER_DEPARTMENT_LOG tdl
WHERE DATEPART(YEAR,tdl._AddingDate)=2017 AND td.[_IDX]>=tdl._BeginIndex
AND td._IDX<=tdl._EndIndex

SELECT t.ID,a.ClassCode,a.LessonName
FROM TEACHER t
LEFT OUTER JOIN
(SELECT c.ManagerID,l.LessonName,c.ClassCode,tcl.TeacherID
FROM TEACHER_CLASS_LESSON tcl,LESSON l,CLASS c
WHERE tcl.LessonCode= l.LessonCode AND c.ClassCode=tcl.ClassCode) a
ON a.ManagerID=t.ID AND a.TeacherID=t.ID
ORDER BY t.ID