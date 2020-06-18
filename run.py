from datetime import datetime, timedelta
import zensheets as zs
import configparser


config = configparser.ConfigParser()
config.read('config.ini')
# import source file
DOMAIN = config['zendesk']['Domain']
CREDS = config['zendesk']['Credentials']
AUTH = config['gsheets']['ServiceFile']
SHEET_NAME = config['gsheets']['SheetName']


def main():
    today = datetime.date(datetime.now())

    presets = configparser.ConfigParser()
    presets.read('presets.ini')
    if presets['DEFAULT']['Period'] == 'W':
        start_date = (today - timedelta(days=8)).strftime("%Y-%m-%d")
        end_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")

    tags = "technical"
    form = "Games"
    sortby = ("created_at","desc")

    query = zs.ZenQuery(domain=DOMAIN, creds=CREDS,to_date=end_date, from_date=start_date,
                        tags=tags, form=form, sortby=sortby)
    tickets = query.get_results()
    f_tickets = query.format_tickets()

    zsheet = ZenOut(f_tickets)
    zsheet.to_gsheets(auth=AUTH, name=SHEET_NAME)
    # this line is a test to make sure
    # that progress is being Saved
    
    return 0


if __name__=="__main__":
    main()
