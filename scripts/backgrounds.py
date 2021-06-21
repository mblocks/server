# -*- coding: utf-8 -*-
import time
import requests
from app.services.streams import append as xadd, read as xread, done as xdone, init as xinit



class Actions:
    def refresh(self, payload):
        response = requests.post('http://127.0.0.1/hello', json=payload)
        print(response)
        return True

def main() -> None:
    xinit(['common'])
    actions = Actions()
    
    while True:
        data = xread('common','hello', is_deliver=True, block=2000)
        if len(data) == 0:
            data = xread('common','hello', is_deliver=False, block=2000)
        for item in data:
            dispatch = item.get('dispatch')
            payload =  item.get('payload')
            try:
                result = getattr(actions, dispatch)(payload)
                if result == True:
                    xdone(consumer_group=item.get('consumer_group'),
                          stream=item.get('stream'),
                          id=item.get('id')
                    )
            except Exception:
                print('fail', item)
        time.sleep(10)


if __name__ == "__main__":
    main()
