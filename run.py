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


# TODO: Exception handling


def main():
    presets = configparser.ConfigParser()
    presets.read('presets.ini')

    start_date, end_date = get_dates(presets['DEFAULT']['Period'].strip('"'))
    sortby = (presets['DEFAULT']['SortBy'].strip('"'),
                presets['DEFAULT']['SortOrder'].strip('"'))
    dyquery = None
    output = False
    # if an argument is provided
    if len(sys.argv) == 2:
        # use argument as name of preset label
        tags = presets[sys.argv[1]]['Tags'].strip('"')
        form = presets[sys.argv[1]]['Form'].strip('"')
        sheet_name = presets[sys.argv[1]]['SheetName'].strip('"')
        query = zs.ZenQuery(domain=DOMAIN, creds=CREDS, to_date=end_date,
            from_date=start_date, tags=tags, form=form, sortby=sortby)
    elif len(sys.argv) > 2:
        dyquery, output = cli_to_query(sys.argv, (start_date, end_date))
        sheet_name = "Gsheets Test v1.33.7" # test
        query = zs.ZenQuery(domain=DOMAIN, creds=CREDS, dyin=dyquery, dyout=output)
    else: # else use test data
        tags = DOMAIN
        form = 'Technical'
        sheet_name = "Gsheets Test v1.33.7"
        query = zs.ZenQuery(domain=DOMAIN, creds=CREDS, to_date=end_date,
            from_date=start_date, tags=tags, form=form, sortby=sortby)

    tickets = query.get_results()
    f_tickets = query.format_tickets()

    zsheet = zs.ZenOut(zq=f_tickets)
    zsheet.to_gsheets(auth=AUTH, name=sheet_name)
    zsheet.to_csv()

    return 0 # zsheet.df

# Helpers
def get_dates(tf):
    start_date = end_date = 0
    #print(start_date, end_date)
    today = datetime.date(datetime.now())
    if tf == 'M': # 1 Month
        start_date = (today - timedelta(days=31)).strftime("%Y-%m-%d")
        end_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    elif tf == 'W': # 1 Week
        start_date = (today - timedelta(days=8)).strftime("%Y-%m-%d")
        end_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    elif tf == 'D': # 1 Week
        start_date = (today - timedelta(days=2)).strftime("%Y-%m-%d")
        end_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        start_date = (today - timedelta(days=8)).strftime("%Y-%m-%d")
        end_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    print(start_date, end_date)
    return start_date, end_date

def cli_to_query(args, dates):
    query_obj = {'domain': None, 'creds': None, 'to_date': None,
                    'from_date': None, 'tags': None, 'form': None, 'group': None,
                    'brand': None, 'text': None, 'status': None, 'sortby': None}
    out_list = None
    for arg in args[1:]: # everything after the script name
        k,v = arg.split('=')
        v = v.strip('"')
        if k.lower() in query_obj.keys():
            query_obj[k] = str(v)#.replace('-','')
        elif k.lower() == 'out':
            out_list = list(v.strip('[]').split(','))
        else:
            print('Argument: {0} Not Valid!'.format(k))
            return -1
    query_obj['from_date'] = dates[0] if query_obj['from_date'] == None else query_obj['from_date']
    query_obj['to_date'] = dates[1] if query_obj['to_date'] == None else query_obj['to_date']
    return query_obj, out_list


if __name__=="__main__":
    main()
