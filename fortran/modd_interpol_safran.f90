MODULE MODD_INTERPOL_SAFRAN
    !! Declarations of namelist variables
    !! Author:
    !! Sabine Radanovics
    !! Date:
    !! 26/10/2020
    IMPLICIT NONE

    LOGICAL :: LMULTIINPUT = .FALSE.
    LOGICAL :: LMULTIOUTPUT = .FALSE.
    LOGICAL :: LTIMECHUNK = .FALSE.
    INTEGER :: NNUMBER_INPUT_FILES = 1
    INTEGER :: NNUMBER_OUTPUT_GRIDS = 1
    INTEGER :: NLONCHUNKSIZE = 115
    INTEGER :: NLATCHUNKSIZE = 115
    CHARACTER(LEN=100) :: HFILEIN
    CHARACTER(LEN=100) :: HFILEOUT
    CHARACTER(LEN=100) :: HGRIDIN
    CHARACTER(LEN=100), DIMENSION(:), ALLOCATABLE :: HFILESIN, HFILESOUT, HGRIDSIN



END MODULE MODD_INTERPOL_SAFRAN