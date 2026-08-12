from tbot223_base import Result, ResultStatus

missing_data: Result[int] = Result(ResultStatus.SUCCESS)
wrong_data: Result[int] = Result(ResultStatus.SUCCESS, None, None, "wrong")
raw_make = Result._make([ResultStatus.SUCCESS, None, None, 1])
raw_replace = Result.ok(1)._replace(data="wrong")
