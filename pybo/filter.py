def format_datetime(value, fmt='%Y년 %m월 %d일 %H:%M'):
    return value.strftime(fmt) # datetime 객체를 문자열로 만들어 반환