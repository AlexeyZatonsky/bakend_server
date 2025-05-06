Неисполняемый шаблон скрипта для загрузки аватара

curl.exe ^
  -X PUT ^
  -H "Content-Type: image/png" ^
  -H "x-amz-acl: public-read" ^
  --upload-file .\avatar.png ^
  