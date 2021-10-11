# Описание kad-service

Для запуска парсинга необходимо направить POST запрос на адрес "/kad-service/" с параметрами вида:
{'participant': '',
 'judge': '',
 'court': '',
 'num': '',
 'datefrom': '',
 'dateto': ''}


'datefrom' и 'dateto' необходимо передовать в следующем формате: dd.mm.yyyy

При фильтрации по дате необходимо передавать оба параметра (datefrom и dateto).

В случае корректной выгрузки информации с сайта в ответе будут данные вида:
[{'court': '',
  'delo': '',
  'delotype': '',
  'plaintiff': '',
  'respondent': [''],
  'url': ''},
 {вторая запись},
 {и т.д.}]
