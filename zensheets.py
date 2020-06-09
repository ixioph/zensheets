import pandas as pd
import pygsheets
import requests
class ZenQuery():
    tickets = None
    formatted = None
    df = None
    def __init__(self, domain, creds, view=None, text=None, status=None,
                 to_date=None, from_date=None, tags=None, form=None,
                 group=None, sortby=None):
        self.domain = domain
        self.header = {'Authorization': f'Basic {creds}'}
        if view != None:
            self.view = view
            self.kind = 'VIEW'
        else:
            if text != None:
                self.text = text
            if status != None:
                self.status = status
            if to_date != None:
                self.to_date = to_date
            if from_date != None:
                self.from_date = from_date
            if tags != None:
                self.tags = tags
            if form != None:
                self.form = form
            if group != None:
                self.group = group
            if sortby != None:
                self.sortby = sortby

            self.kind = 'SEARCH'
            self.build_url()


    def get_results(self):
        try:
            r = requests.get(self.url, headers=self.header)
            if (r.status_code == 200):
                print('Query Retrieval Successful!\n')
                response = json.loads(str(r.text))
                count = response['count']
                self.tickets = response['results']
                if response['next_page'] is not None:
                    if 'page=11' not in response['next_page']:
                        new_self.tickets = self.get_results(response['next_page'])
                        self.tickets = self.tickets + new_self.tickets
                    else:
                        last_ticket = self.tickets[len(self.tickets)-1]
                        last_ticket_date = str(last_ticket['created_at']).split('T')[0]
                        print('paginating from.. ', last_ticket_date)
                        self.to_date = last_ticket_date
                        self.from_date = None
                        self.sortby = '&sort_by=created_at&sort_order=desc'
                        self.build_url()
                        new_self.tickets = self.get_results(self.url)
                        self.tickets = self.tickets + new_self.tickets
                return self.tickets
            else:
                print(str(r.status_code), r.text)
        except Exception as e:
            print(str(e))
            return None
        return 0

    def get_url(self):
        return self.url

    def build_url(self):
        self.query = self.text + self.status #...
        url_string = 'https://{0}.zendesk.com/api/v2/search.json?query={1}'.format(self.domain, self.query)
        self.url = url_string
        return 0

    def create_blank_response_obj(self):
        obj = {
            'ticket_id': '',
            'ticket_url': '',
            'date': '',
            'game': None,
            'device_type': None,
            'issue_type': None,
            'tags': '',
            #'escalation_status': False,
            'status': ''
        }
        return obj

    def format_tickets(self, custom=None):
        if self.tickets != None:
            objlist = []
            for ticket in self.tickets:
                obj = self.create_blank_response_obj()
                tick_id = str(ticket['id'])
                tick_id = '=HYPERLINK("{0}{1}", "{1}")'.format("https://crunchyroll.zendesk.com/agent/tickets/", tick_id)
                obj['ticket_id'] = tick_id
                obj['ticket_url'] = 'https://crunchyroll.zendesk.com/agent/tickets/' + str(ticket['id'])
                date = datetime.strptime(ticket['created_at'],"%Y-%m-%dT%H:%M:%SZ")
                obj['date'] = date.strftime("%Y-%m-%d")

                if custom != None:
                    for custom_field in ticket['custom_fields']:
                        if str(custom_field['id']) not in custom.keys():
                            continue
                        else:
                            obj[str(custom[str(custom_field['id'])])] = custom_field['value']
                # update escalation status
                if 'escalated_games' in ticket['tags']:
                    obj['escalation_status'] = True
                obj['status'] = ticket['status']
                objlist.append(obj)
            self.formatted = objlist
            return objlist



class ZenOut():
    def __init__(self, zq):
        self.df = pd.DataFrame(zq.formatted)
        return self.out

    def to_csv(self, fname='a'):
        try:
            self.df.to_csv(f'./{fname}.csv')
            print(f'Saved CSV to:: ./{fname}.csv!')
            return 0
        except Exception as e:
            print(f'ERROR :: {e}')
            return -1

    def to_pickle(self, fname='a'):
        try:
            self.df.to_pickle(f'./{fname}.pkl')
            print(f'Saved Pickle to:: ./{fname}.pkl!')
            return 0
        except Exception as e:
            print(f'ERROR :: {e}')
            return -1

    def to_gsheets(self, auth=None, name=None, page=0):
        assert auth != None, 'Provide a service file.'
        assert name != None, 'Provide a sheet name.'
        try:
            self.gsheet_auth = pygsheets.authorize(service_file=auth)
            self.gsheets = gc.open(name)
            self.gsheet = self.gsheets[page]
            # clear sheet
            self.gsheet.set_dataframe(self.df, (1,1))
            return 0
        except Exception as e:
            print(str(e))
            return -1














### EOF
