'''
Created on 02.12.2021

@author: Artem_Petrov
'''

import csv
import argparse

    
class Pattern_A():
        
    is_initialized = False
    events = []
    alert_template = '[{}] ALERT: Pattern A: start: {} end: {}  count: {} [message, speed]: {}'
        
    def is_coming(self, event):
        return event[2] == 'coming'
        
        
    # process event with message 1339
    def initialize(self, event):
        '''
        Process an 1339 event. (De-) initialize the pattern 
        '''
        
        # activate
        if self.is_coming(event):
            if not self.is_initialized:
                self.is_initialized = True
                return True
                    
            else:
                # ERROR: Pattern A was initialized, but 1339 coming received, nothing to do
                return False
        # deactivate
        else:
            if self.is_initialized:
                self.is_initialized = False
                return True
            else:
                # ERROR: Pattern A was not initialized, but 1339 going received, nothing to do
                return False
        
        
    def consume_event(self, event):
        '''
        Consumes an event. Fist, check if this a 1339, 2118 or 4948 message. 
        If 1339 then (de-) initialize the pattern.
        Next process event.
        '''
        
        message = int(event[1])
        alert = ''
            
        if message == 1339:
            if self.initialize(event):
                alert = self.process_event(event)
                
        if self.is_coming(event) and message in (2118, 4948):
            if self.is_initialized:
                alert = self.process_event(event)
                    
        return alert
            
            
    def process_event(self, event):
        '''
        Process an event. When the pattern was deinitialized (in consume event), then clear list incoming events
        '''
        
        self.events.append(event)
        alert = self.print_alert()
        # end of life cycle, 1339 going received
        if not self.is_initialized:
            self.events.clear()
               
        return alert
                
                
    def get_relevant_messages(self):
        '''
        Filter list of events (ignore 1339 messages) and extract only message number and speed.
        Get time stamp from last event
        
        @return: timestamp of last event and list of relevant messages
        '''
        
        relevant_events = []
        timestamp = ''
        if len(self.events) > 1:
            relevant_events = self.events[1:]
            if relevant_events:
                timestamp = relevant_events[-1][0]
        if len(relevant_events) and int(relevant_events[-1][1]) == 1339:
            relevant_events = relevant_events[:-1]
                
        relevant_messages = []
        for e in relevant_events:
            relevant_messages.append([e[1], e[3]])
            
                
        return timestamp, relevant_messages
        
                
    def print_alert(self):
        '''
        Generates an alert, if messages 2118 or 4948 (direction coming) occur of if pattern A goes inactive (1339 going)
        '''
        
        alert = ''
        start = int(self.events[0][0])
        end = -1
        last_event = self.events[-1]
        if int(last_event[1]) == 1339 and len(self.events) > 1:
            end = int(last_event[0])
            
        timestamp, relevant_messages = self.get_relevant_messages()
            
        # print if only messages received
        if (len(relevant_messages)):
            alert = self.alert_template.format(timestamp, start, end, len(relevant_messages), relevant_messages)
            
        return alert


class Pattern_B():
        
    is_initialized = False
    start_gross = 0
    current_gross = 0

    start_ts = 0
    end_ts = 0
    
    alert_template = '[{}] ALERT: Pattern B: start: {} end: {}  gross (1339 inactive): {} gross (1748 active): {}'
        
    def is_coming(self, event):
        return event[2] == 'coming'
        
        
    def initialize(self, event):
        '''
        Initialize the pattern: 
        1. actualize current gross
        2. deinitialize the pattern, after 50 gross sheets
        3. initialize the pattern if 1339 going received
        '''
        
        message = int(event[1])
        
        if self.is_coming(event):
            self.current_gross = int(event[-1])
            
            # deactivate if 
            if self.is_initialized and self.current_gross - self.start_gross > 50:
                self.is_initialized = False
                self.end_ts = 0
        
        # 1339 going
        elif message == 1339:
            # reset gross counter and initialize
            self.is_initialized = True
            self.start_gross = self.current_gross
            self.start_ts = int(event[0])
                
    
    def consume_event(self, event):
        '''
        Consume event:
        1. (de-) initialize the pattern
        2. if the pattern is active and 1748 coming received, than process event
        '''
        
        message = int(event[1])
        alert = ''
        
        self.initialize(event)
        
        if self.is_initialized and message == 1748 and self.is_coming(event):
            alert = self.process_event(event)
            
        return alert
    
    
    def process_event(self, event):
        '''
        Process an 1748 incoming event and generate alert
        '''
        
        # set time stamp of the first 1748 becoming active
        if not self.end_ts:
            self.end_ts = int(event[0])
            
        event_gross = int(event[-1])
        timestamp = int(event[0])
        
        alert = self.alert_template.format(timestamp, self.start_ts, self.end_ts, self.start_gross, event_gross)
        
        return alert
            

class Consumer():
    
    alerts = []
    
    def __init__(self):
        self.patterns = [Pattern_A(), Pattern_B()]
        
    
    def get_alerts(self):
        return self.alerts
    
    
    def consume_event(self, event):
        '''
        Consume event and pass it to both patterns. 
        Write alert t
        '''
        
        for pattern in self.patterns:
            alert = pattern.consume_event(event)
            if alert:
                self.alerts.append(alert)
        

def read_data(path):
    
    with open(path, newline='') as csvfile:
        datareader = csv.reader(csvfile)
        data = list(datareader)

        # ignore first line with comments
        return data[1:]


def write_data(path, data):
    with open(path, 'w') as f:
        for item in data:
            f.write("%s\n" % item)


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Analyze data flow.')
    parser.add_argument('-i', '--input_file', type=str, help='input file', required=True)
    parser.add_argument('-o', '--output_file', type=str, help='output file', required=True)
    
    args = parser.parse_args()
    
    input_data_path = args.input_file
    output_data_path = args.output_file
    
    events = read_data(input_data_path)
    consumer = Consumer()
    
    # process all events sequentially
    for event in events:
        consumer.consume_event(event)
        
    write_data(output_data_path, consumer.get_alerts())