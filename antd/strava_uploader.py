import requests
import antd.plugin as plugin
import logging

_log = logging.getLogger("antd.strava_uploader")
strava_url = "https://www.strava.com/api/v3/"



class StravaUploader(plugin.Plugin):
    
    key = None
    
    def data_available(self, device_sn, format, files):
        if format not in ("tcx"): return files
        result = []
        
        try:
            for file_name in files:
                self.upload(file_name, format)
                result.append(file_name)
        except:
            pass
        
        return files
        
        
        
    def upload(self, file_name, format):
        _log.info("Uploading %s to Strava via API.", file_name)
        f = file(file_name)
        
        activity_name = raw_input("Please enter the activity name: ")
        description = raw_input("Please enter a description.")
        
        params = {"access_token": self.key,
                  "activity_type": "run",
                  "data_type": format,
                  "name": activity_name,
                  "description": description
                  }
        
        r = requests.post(strava_url+"uploads", params=params, files={"file": f})
        if r.status_code == 201:
            _log.info("Activity uploaded successful.")
            try: _log.info("Strava API: %s" % r.json()["status"])
            except: pass
        else:
            try: _log.error("Strava API: %s" % r.json()["error"])
            except: _log.error("There was an unknown error uploading to Strava.")
        return r