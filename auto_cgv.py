import subprocess
import json
import xmltodict
import os
import time

curl_cmd = """curl 'http://ticket.cgv.co.kr/CGV2011/RIA/CJ000.aspx/CJ_002_PRIME_ZONE_LANGUAGE' -H 'Accept: application/json, text/javascript, */*; q=0.01' -H 'Referer: http://ticket.cgv.co.kr/Reservation/Reservation.aspx?MOVIE_CD=&MOVIE_CD_GROUP=&PLAY_YMD=&THEATER_CD=&PLAY_NUM=&PLAY_START_TM=&AREA_CD=&SCREEN_CD=&THIRD_ITEM=' -H 'Origin: http://ticket.cgv.co.kr' -H 'X-Requested-With: XMLHttpRequest' -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36' -H 'Content-Type: application/json' --data-binary '{"REQSITE":"x02PG4EcdFrHKluSEQQh4A==","Language":"zqWM417GS6dxQ7CIf65+iA==","TheaterCd":"2ziBKjUqqpsaZ8ii0eHHyg==","PlayYMD":"%s","ScreenCd":"DTOy6NZjL7Nd6/QAUh7m7g==","PlayNum":"%s"}' --compressed 2>/dev/null ;"""

starting_time={
        7:"H+diKGhh/2VXj/6Ikiev8A==",
        10:"eUHdeAgG0OAi96HPh0I1jQ==",
        13:"hlrIVsrgDYMr7PQdmwAA4w==",
        17:"K69H87N+CcalH4eFao/hAQ==",
        20:"GQ4XBvPgo294+v/kGdDx+Q==",
        24:"LP1Md9chfBBpfDnclOyDHw=="
}

YMD={
        510 :"K49Pa7i2tgGLdOsDEUNQ0g=="
#        511 :"+cSU7ax/NJV5XNsYM3QrKA==",
#        512 :"JFQ+RQXJ8Uin2E/NDXx6+Q==",
#        513 :"8zytF40Cbdzd+E+B/DtRwQ=="
        }

class CGVSeatInfo() :

  def __init__(self) :
    self.request_cmd_dict = dict()
    for ymd in YMD.keys() :
        for start in starting_time.keys() :
            datetime = "%d월 %d일 %d시" % (ymd//100, ymd%100, start)
            cur_req_cmd = curl_cmd % (YMD[ymd], starting_time[start])
            self.request_cmd_dict[datetime] = cur_req_cmd
    self.royal_seats = dict()
    self.reservation_info = dict()
    self.seat_str = dict()
    for datetime in self.request_cmd_dict.keys():
      self.royal_seats[datetime] = []
      self.reservation_info[datetime] = []
      self.seat_str[datetime] = []

  def update_seat_info(self) :
    for datetime in self.request_cmd_dict.keys() :
      time.sleep(0.5)
      request_cmd = self.request_cmd_dict[datetime]
      seat_info_list = self.reservation_info[datetime] = self.get_seat_info_with_cmd(request_cmd)
      self.royal_seats[datetime] = self.get_royal_seats(seat_info_list)
      self.seat_str[datetime] = self.get_seat_info_str(seat_info_list)

  def get_royal_seats(self, seat_info_list) :
    royal_seats = []

    if seat_info_list == None :
      return None
    for seat_item in seat_info_list :
      if seat_item[2] == "Y" and self.isFuckingAbsolutelySupurPowerfulDefinitlySuccessfulRoyalSeat(seat_item) :
        royal_seats.append(seat_item)

    return royal_seats

  def get_seat_info_with_cmd(self, request_cmd) :
    req_str = subprocess.check_output(request_cmd, shell=True)
    raw_json_data = json.loads(req_str)
    seat_info_xml = raw_json_data["d"]["data"]["DATA"]
    new_data_set = json.loads(json.dumps(xmltodict.parse(seat_info_xml), indent=4))["NewDataSet"]
    if "SEAT_INFO" in new_data_set.keys() :
      seat_info_dict = new_data_set["SEAT_INFO"]
    else :
      return None
    seat_info_list = [(int(seat["LOC_X"]), int(seat["LOC_Y"]), seat["SEAT_STATE"]) for seat in seat_info_dict]
    return seat_info_list

  def get_seat_info_str(self, seat_info_list) :
    if seat_info_list == None :
      return ""
    max_row = 13
    max_col = 36

    col_info = "".join(["%3d" % i for i in range(1, max_col)])
    row_info = " ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    seat_info = [["   " for i in range(1, 36)] for j in range(max_row)]

    for seat_item in seat_info_list :
      if seat_item[2] == "N" :
        seat_info[seat_item[1]-1][seat_item[0]-1] = "  !"
      else :
        seat_info[seat_item[1]-1][seat_item[0]-1] = "  @"

    row_strings = [col_info] + ["".join(row) for row in seat_info]
    row_strings_with_row_info = []
    for idx, row in enumerate(row_strings) :
      row_strings_with_row_info.append(row_info[idx]+ "  " + row)
    return "\n".join(row_strings_with_row_info)

  def printAllSeat(self) :
    previous_royal_seat_cnt = sum([len(self.royal_seats[key]) if self.royal_seats[key] != None else 0 for key in self.royal_seats.keys()])
    self.update_seat_info()
    str_to_print = "\n".join([key+"\n"+self.seat_str[key] for key in self.seat_str.keys()])
    print(str_to_print)

    current_royal_seat_cnt = sum([len(self.royal_seats[key]) if self.royal_seats[key] != None else 0 for key in self.royal_seats.keys()])
    #if previous_royal_seat_cnt != current_royal_seat_cnt :
    print(str_to_print)

  def printRoyalSeat(self) :
    self.update_seat_info()
    royal_seat_cnt = [len(self.royal_seats[key]) if self.royal_seats[key] != None else 0 for key in self.royal_seats.keys()]
    str_to_print = "\n".join([key+"\n"+self.seat_str[key] for idx, key in enumerate(self.seat_str.keys()) if royal_seat_cnt[idx] > 0])
    print(str_to_print)

  def isFuckingAbsolutelySupurPowerfulDefinitlySuccessfulRoyalSeat(self, seat_info) :
    return 36/2 - 7 < seat_info[0] < 36/2 + 7 and 4 < seat_info[1] < 20

def main() :
  cgv_crawler = CGVSeatInfo()
  while(1) :
    cgv_crawler.printRoyalSeat()
    time.sleep(3)

main()
