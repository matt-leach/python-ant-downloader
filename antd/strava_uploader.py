import requests
import antd.plugin as plugin
import logging
import time

_log = logging.getLogger("antd.strava_uploader")
strava_url = "https://www.strava.com/api/v3/"


class StravaUploader(plugin.Plugin):

    key = None

    def data_available(self, device_sn, format, files):
        if format not in ("tcx"):
            return files
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
        description = raw_input("Please enter a description: ")

        params = {"access_token": self.key,
                  "activity_type": "run",
                  "data_type": format,
                  "name": activity_name,
                  "description": description
                  }

        r = requests.post(strava_url+"uploads", params=params, files={"file": f})
        if r.status_code != 201:
            try:
                _log.error("Strava API: %s" % r.json()["error"])
            except:
                _log.error("There was an unknown error uploading to Strava.")
            return

        # Continue if no error
        _log.info("Strava API: %s" % r.json()["status"])
        activity_upload_id = r.json()['id']
        add_gear = raw_input("Type 'yes' if you would like to add gear to this activity. ")
        if add_gear != 'yes':
            return

        # Get the athlete and print the gear
        r = requests.get(strava_url+"athlete", params={"access_token": self.key})
        strava_athlete = r.json()
        for gear in strava_athlete['shoes']:
            print gear['id'], gear['name']
        for gear in strava_athlete['bikes']:
            print gear['id'], gear['name']

        gear_id = raw_input("Type the id of the gear you used during the activity: ")

        while True:
            # Poll the uploads endpoint to see if the activity has uploaded
            r = requests.get(strava_url+"uploads/"+activity_upload_id)
            _log.info("Strava API: %s" % r.json()["status"])
            activity_id = r.json()['activity_id']
            if activity_id:
                break
            _log.info("Sleeping for 5s before polling")
            time.sleep(5)

        # Now we have the activity id we update it
        params = {"access_token": self.key, "gear_id": gear_id}
        r = requests.put(strava_url+"activities/"+activity_id, params=params)
        print r.json(), r.status_code
