from datetime import datetime
import pandas as pd
import pygsheets
import requests
import json

# TODO: Dynamically formatted output
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
            return
        else:
            ## TODO: remove hardcoded spaces
            self.query = ""
            if text != None:
                self.text = text
                self.query = text
            if tags != None:
                self.tags = tags
                if self.query != "":
                    self.query += ' '
                self.query += 'tags:{0}'.format(tags)
            if form != None:
                self.form = form
                self.query += ' form:{0}'.format(form)
            if group != None:
                self.group = group
                self.query += ' group:{0}'.format(group)
            if status != None:
                self.status = status
                self.query += ' status:{0}'.format(status)
            if from_date != None:
                self.from_date = from_date
                self.query += ' created>{0}'.format(from_date)
            if to_date != None:
                self.to_date = to_date
                self.query += ' created<{0}'.format(to_date)
            if sortby != None:
                self.sortby = sortby
                self.query += '&sort_by={0}&sort_order={1}'.format(sortby[0], sortby[1])
            else:
                # sort by default
                self.query += '&sort_by=created_at&sort_order=desc'

            self.kind = 'SEARCH'
            self.build_url()
            print(self.url)


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
                        self.url = response['next_page']
                        new_tickets = self.get_results()
                        self.tickets = self.tickets + new_tickets
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
        url_string = 'https://{0}.zendesk.com/api/v2/search.json?query={1}'.format(self.domain, self.query)
        self.url = url_string
        return 0

    def create_blank_response_obj(self):
        obj = {
            'ticket_id': '',
            #'ticket_url': '',
            'date': '',
            'subject': '',
            #'game': None,
            #'device_type': None,
            #'issue_type': None,
            'tags': '',
            #'escalation_status': False,
            'status': ''
        }
        return obj

    # TODO: Evaluate I/O
    def format_tickets(self, custom=None):
        if self.tickets != None:
            objlist = []
            for ticket in self.tickets:
                obj = self.create_blank_response_obj()
                tick_id = str(ticket['id'])
                tick_domain = "https://{0}.zendesk.com/agent/tickets/".format(self.domain)
                tick_id = '=HYPERLINK("{0}{1}", "{1}")'.format(tick_domain, tick_id)
                obj['ticket_id'] = tick_id
                #obj['ticket_url'] = tick_domain + str(ticket['id'])
                date = datetime.strptime(ticket['created_at'],"%Y-%m-%dT%H:%M:%SZ")
                obj['date'] = date.strftime("%Y-%m-%d")

                obj['subject'] = str(ticket['subject'])
                obj['tags'] = str(ticket['tags'])

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
    def __init__(self, zq=None):
        if zq != None:
            self.df = pd.DataFrame(zq)
        else:
            print('ZenQuery object required.')

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
            self.gsheets = self.gsheet_auth.open(name)
            self.gsheet = self.gsheets[page]
            # clear sheet
            self.gsheet.set_dataframe(self.df, (1,1))
            print('Posted successfully to: ', name, page)
            return 0
        except Exception as e:
            print(str(e))
            return -1

    def to_jira(self):
        return 0














### EOF
