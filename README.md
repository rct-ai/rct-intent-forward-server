# rct-intent-forward-server
意图转发服务

# 启动方式
docker-compose -f docker-compose.yml up -d

## dataprocess 
```angular2html
 python utils/process_data.py --tasks sanji --csv_path intent_table.csv --json_path ./intent_sanji.json

python utils/process_data.py --tasks csv2json --csv_path intent_all.csv --json_path ./intent.json


```