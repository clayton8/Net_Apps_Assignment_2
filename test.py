from ZeroconfService import ZeroconfService
import time
 
service = ZeroconfService(name="Joe's awesome FTP server",
                          port=3000,  stype="_ftp._tcp")
service.publish()
time.sleep(10)
service.unpublish()

