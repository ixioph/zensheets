from datetime import datetime, timedelta
import zensheets as zs

# import source file
DOMAIN =
CREDS =

def main():
    today = datetime.date(datetime.now())
    start_date = (today - timedelta(days=8)).strftime("%Y-%m-%d")
    end_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    tags = "mass_for_the_dead"
    form = "Games"
    sortby = ("created_at","desc")

    query = zs.ZenQuery(domain=DOMAIN, creds=CREDS,to_date=end_date, from_date=start_date,
                        tags=tags, form=form, sortby=sortby)
    return 0


if __name__=="__main__":
    main()
