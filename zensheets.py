from datetime import datetime
import pandas as pd
import pygsheets
import requests
import base64
import json

# TODO: Dynamically formatted output not
class ZenQuery():
    tickets = None
    formatted = None
    df = None
    out_format = ['id', 'created_at', 'subject', 'tags', 'status']
    def __init__(self, domain, creds, dyin=False, dyout=False, view=None, text=None, status=None,
                 to_date=None, from_date=None, tags=None, form=None, brand=None,
                 group=None, sortby=None, email=None, name=None):
        self.domain = domain
        self.header = {'Authorization': f'Basic {creds}'}
        self.query = ""

        if dyout != False and dyout != None:
            self.out_format = dyout
            print("Output Format:", self.out_format)

        if view != None:
            self.view = view
            self.kind = 'VIEW'
            return 0
        elif dyin != False:
            self.kind = 'CUSTOM'
            # do the things with DYQUERY OBJ. parse and shit, yo
            # for k in dyin.keys():
            #     setattr(?, k, dyin[k]) # k to obj?
            self.process_dynamic_in(dyin)
        else:
            ## TODO: remove hardcoded spaces and clean up this garbage
            if text != None:
                self.text = text
                self.query = text
            if tags != None:
                self.tags = tags
                if self.query != "":
                    self.query += ' '
                self.query += 'tags:{0}'.format(self.tags)
            if form != None:
                self.form = form
                self.query += ' form:{0}'.format(self.form)
            if group != None:
                self.group = group
                self.query += ' group:{0}'.format(self.group)
            if status != None:
                self.status = status
                self.query += ' status:{0}'.format(self.status)
            if from_date != None:
                self.from_date = from_date
                self.query += ' created>{0}'.format(self.from_date)
            if to_date != None:
                self.to_date = to_date
                self.query += ' created<{0}'.format(self.to_date)
            if sortby != None:
                self.sortby = sortby
                self.query += '&sort_by={0}&sort_order={1}'.format(self.sortby[0], self.sortby[1])
            else:
                # sort by default
                self.query += '&sort_by=created_at&sort_order=desc'

            self.kind = 'SEARCH'
        self.build_url()
        print(self.url)

    # TODO: this function is fucking ugly
    def process_dynamic_in(self, dyin):
        if dyin['text'] != None:
            self.text = dyin['text']
            self.query = dyin['text']
        if dyin['tags'] != None:
            self.tags = dyin['tags']
            if self.query != "":
                self.query += ' '
            self.query += 'tags:{0}'.format(self.tags)
        if dyin['form'] != None:
            self.form = dyin['form']
            self.query += ' form:{0}'.format(self.form)
        if dyin['brand'] != None:
            self.brand = dyin['brand']
            self.query += ' brand:{0}'.format(self.brand)
        if dyin['group'] != None:
            self.group = dyin['group']
            self.query += ' group:{0}'.format(self.group)
        if dyin['status'] != None:
            self.status = dyin['status']
            self.query += ' status:{0}'.format(self.status)
        if dyin['from_date'] != None:
            self.from_date = dyin['from_date']
            self.query += ' created>{0}'.format(self.from_date)
        if dyin['to_date'] != None:
            self.to_date = dyin['to_date']
            self.query += ' created<{0}'.format(self.to_date)
        if dyin['sortby'] != None:
            self.sortby = dyin['sortby']
            self.query += '&sort_by={0}&sort_order={1}'.format(self.sortby[0], self.sortby[1])
        else:
            # sort by default
            self.query += '&sort_by=created_at&sort_order=desc'
        #return 0


    def get_results(self):
        try:
            r = requests.get(self.url, headers=self.header)
            if (r.status_code == 200):
                print('Page Retrieval Successful!', self.url)
                response = json.loads(str(r.text))
                count = response['count']
                self.tickets = response['results']
                if response['next_page'] is not None:
                    if 'page=11' not in response['next_page']:
                        self.url = response['next_page']
                        curr_tickets = self.tickets
                        new_tickets = self.get_results()
                        self.tickets = curr_tickets + new_tickets
                    else:
                        last_ticket = self.tickets[len(self.tickets)-1]
                        last_ticket_date = str(last_ticket['created_at']).split('T')[0]
                        print('PAGE 11 REACHED ')
                        print('paginating to.. ', last_ticket_date)
                        temp_url = self.url
                        temp_url=temp_url.replace(self.to_date, last_ticket_date)
                        temp_url=temp_url.replace('page=10&', '')
                        #print('TEMP URL: ', temp_url)
                        self.to_date = last_ticket_date
                        self.from_date = None
                        self.sortby = '&sort_by=created_at&sort_order=desc' # new_self
                        self.url = temp_url
                        new_tickets = self.get_results()
                        self.tickets = self.tickets + new_tickets
                return self.tickets
            else:
                print(str(r.status_code), r.text)
        except Exception as e:
            print(str(e))
            return None
        #return 0

    def get_url(self):
        return self.url

    def build_url(self):
        url_string = 'https://{0}.zendesk.com/api/v2/search.json?query={1}'.format(self.domain, self.query)
        self.url = url_string
        #return 0

    def create_blank_response_obj(self):
        obj = {}
        for field in self.out_format:
            obj[field] = ''
        #print("Output Object:", obj)
        return obj

    # TODO: Evaluate I/O
    def format_tickets(self, custom=None, userID=True):
        if self.tickets != None:
            objlist = []
            for ticket in self.tickets:
                obj = self.create_blank_response_obj()
                # for every key in the object
                # assign the ticket value of thet field
                # matching that key name to the object
                ##print("Object Keys:", obj.keys())
                for k in list(obj):
                    obj[k] = str(ticket[k])
                    # then, make any necessary formatting changes
                    if k == 'id':
                        tick_url = "https://{0}.zendesk.com/agent/tickets/".format(self.domain)
                        tick_url = '=HYPERLINK("{0}{1}", "{1}")'.format(tick_url, obj[k])
                        obj[k] = tick_url
                    if k == 'created_at':
                        date = datetime.strptime(obj[k],"%Y-%m-%dT%H:%M:%SZ")
                        obj[k] = date.strftime("%Y-%m-%d")
                    # TODO: move the escalated games mod to another function
                    # where X = tag to look for, y = whether it's found
                    if k == 'tags' and 'escalated_games' in obj[k]:
                        obj['escalated_games'] = True
                # TODO: revisit custom fields
                if custom != None:
                    for custom_field in ticket['custom_fields']:
                        if str(custom_field['id']) not in custom.keys():
                            continue
                        else:
                            obj[str(custom[str(custom_field['id'])])] = custom_field['value']
                if userID and 'address' in ticket['via']['source']['from'].keys():
                    #print(ticket['id'], ticket['via']['source']['from'], bool(ticket['via']['source']['from']))
                    obj['email'] = str(ticket['via']['source']['from']['address'])
                    obj['name'] = str(ticket['via']['source']['from']['name'])
                objlist.append(obj)
            self.formatted = objlist
            return objlist





class ZenOut():
    def __init__(self, zq=None):
        if isinstance(zq, pd.DataFrame): #pandas dataframe:
            self.df = zq
        elif zq != None:
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
            self.gsheet.clear(fields='*')
            self.gsheet.set_dataframe(self.df, (1,1))
            print(f'Posted successfully to: {name} [{page}]')
            return 0
        except Exception as e:
            print(str(e))
            return -1

    def to_jira(self):
        ''' Create a Jira issue for each ticket or group of tickets'''
        return 0

    def to_zendesk(self, dom, auth=None):
        ''' Post the given pandas series to a Zendesk ticket, given
            the domain and authentification'''

        zenurl = f'https://{dom}.zendesk.com/api/v2/requests.json'
        #creds = str(auth[0] + '/token:' + auth[1]).encode(encoding='utf_8')
        #creds = base64.b64encode(creds)
        #head = {f'Authorization': f'Basic {creds}'}
        for i,tick in self.df.iterrows():
            #print(tick)
            n = tick['name'] if tick['name'] is not None else "No Name Found"
            e = tick['email'] if tick['email'] is not None else "No Email Found"
            dat0 = {"request": {
                        "requester": {"name": n, "email": e},
                        "subject": str(tick['subject']),
                        "comment": {"body": str(tick['description'])}
                        }
                    }
            print(type(dat0))
            dat0 = json.dumps(dat0)
            print(type(dat0))
            dat0 = json.loads(dat0)
            print(type(dat0), dat0)



            try:
                r = requests.post(zenurl, json=dat0)#, headers=head)

                if (r.status_code == 200):
                    print(r.status_code)
                else:
                    print(r.status_code, r.text, r.headers, r)
            except Exception as e:
                print(str(e))
                return -1
        return r
















### EOF
