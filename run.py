from datetime import datetime, timedelta
import zensheets as zs
import configparser
import sys


config = configparser.ConfigParser()
config.read('config.ini')
# import source file
DOMAIN = config['zendesk']['Domain'].strip('"')
CREDS = config['zendesk']['Credentials'].strip('"')
AUTH = config['gsheets']['ServiceFile'].strip('"')


####### TODO?


def main():
    presets = configparser.ConfigParser()
    presets.read('presets.ini')

    start_date, end_date = get_dates(presets['DEFAULT']['Period'].strip('"'))
    sortby = (presets['DEFAULT']['SortBy'].strip('"'),
                presets['DEFAULT']['SortOrder'].strip('"'))
    dyquery = None
    # if an argument is provided
    if len(sys.argv) == 2:
        # use argument as name of preset label
        tags = presets[sys.argv[1]]['Tags'].strip('"')
        form = presets[sys.argv[1]]['Form'].strip('"')
        sheet_name = presets[sys.argv[1]]['SheetName'].strip('"')
    elif len(sys.argv) > 2:
        dyquery = cli_to_query(sys.argv)
    else: # else use test data
        tags = "issue_buffering"
        form = "Technical"
        sheet_name = "Gsheets Test v1.33.7"

    if dyquery = None:
        query = zs.ZenQuery(domain=DOMAIN, creds=CREDS,to_date=end_date,
            from_date=start_date, tags=tags, form=form, sortby=sortby)
    else:
        query = zs.ZenQuery(dyin=dyquery)

    tickets = query.get_results()
    f_tickets = query.format_tickets()

    zsheet = zs.ZenOut(zq=f_tickets)
    zsheet.to_gsheets(auth=AUTH, name=sheet_name)

    return 0

# Helpers
def get_dates(tf):
    start_date = end_date = 0
    print(start_date, end_date)
    today = datetime.date(datetime.now())
    if tf == 'M': # 1 Month
        start_date = (today - timedelta(days=31)).strftime("%Y-%m-%d")
        end_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    elif tf == 'W': # 1 Week
        start_date = (today - timedelta(days=8)).strftime("%Y-%m-%d")
        end_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        start_date = (today - timedelta(days=8)).strftime("%Y-%m-%d")
        end_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    print(start_date, end_date)
    return start_date, end_date

def cli_to_query(args):
    query_obj = {'domain': None, 'creds': None, 'to_date': None,
                    'from_date': None. 'tags': None, 'form': None, 'group': None,
                    'text': None, 'status': None}
    for arg in args[1:]: # everything after the script name
        k,v = arg.split('=')
            if k in query_obj.keys():
                query_obj[k] = v
            else:
                print('Argument: {0} Not Valid!'.format(k))
                return -1
    return query_obj


if __name__=="__main__":
    main()
