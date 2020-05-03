import subprocess
import json
import xmltodict
import os
import time
from cgv_crypto import CGV_AES

seat_info_cmd = """curl 'http://ticket.cgv.co.kr/CGV2011/RIA/CJ000.aspx/CJ_002_PRIME_ZONE_LANGUAGE' -H 'Accept: application/json, text/javascript, */*; q=0.01' -H 'Referer: http://ticket.cgv.co.kr/Reservation/Reservation.aspx?MOVIE_CD=&MOVIE_CD_GROUP=&PLAY_YMD=&THEATER_CD=&PLAY_NUM=&PLAY_START_TM=&AREA_CD=&SCREEN_CD=&THIRD_ITEM=' -H 'Origin: http://ticket.cgv.co.kr' -H 'X-Requested-With: XMLHttpRequest' -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36' -H 'Content-Type: application/json' --data-binary '{"REQSITE":"x02PG4EcdFrHKluSEQQh4A==","Language":"zqWM417GS6dxQ7CIf65+iA==","TheaterCd":"%s","PlayYMD":"%s","ScreenCd":"%s","PlayNum":"%s"}' --compressed 2>/dev/null ;"""

time_table_cmd = """
curl 'http://ticket.cgv.co.kr/CGV2011/RIA/CJ000.aspx/CJ_HP_TIME_TABLE' -H 'Accept: application/json, text/javascript, */*; q=0.01' -H 'Referer: http://ticket.cgv.co.kr/Reservation/Reservation.aspx?MOVIE_CD=&MOVIE_CD_GROUP=&PLAY_YMD=&THEATER_CD=&PLAY_NUM=&PLAY_START_TM=&AREA_CD=&SCREEN_CD=&THIRD_ITEM=' -H 'Origin: http://ticket.cgv.co.kr' -H 'X-Requested-With: XMLHttpRequest' -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36' -H 'Content-Type: application/json' --data-binary '{"REQSITE":"x02PG4EcdFrHKluSEQQh4A==","MovieGroupCd":"%s","TheaterCd":"%s","PlayYMD":"%s","MovieType_Cd":"/Saxvehmz4RPKZDKNMvSKQ==","Subtitle_CD":"nG6tVgEQPGU2GvOIdnwTjg==","SOUNDX_YN":"nG6tVgEQPGU2GvOIdnwTjg==","Third_Attr_CD":"nG6tVgEQPGU2GvOIdnwTjg==","IS_NORMAL":"nG6tVgEQPGU2GvOIdnwTjg==","Language":"zqWM417GS6dxQ7CIf65+iA=="}' --compressed 2>/dev/null
"""

date_table_cmd = """
curl 'http://ticket.cgv.co.kr/CGV2011/RIA/CJ000.aspx/CJ_HP_SCHEDULE_TOTAL_PLAY_YMD' -H 'Accept: application/json, text/javascript, */*; q=0.01' -H 'Referer: http://ticket.cgv.co.kr/Reservation/Reservation.aspx?MOVIE_CD=&MOVIE_CD_GROUP=&PLAY_YMD=&THEATER_CD=&PLAY_NUM=&PLAY_START_TM=&AREA_CD=&SCREEN_CD=&THIRD_ITEM=' -H 'Origin: http://ticket.cgv.co.kr' -H 'X-Requested-With: XMLHttpRequest' -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36' -H 'Content-Type: application/json' --data-binary '{"REQSITE":"x02PG4EcdFrHKluSEQQh4A==","TheaterCd":"%s","ISNormal":"3y+GIXzg3xKpOjlKjH8+Fg==","MovieGroupCd":"%s","ScreenRatingCd":"nG6tVgEQPGU2GvOIdnwTjg==","MovieTypeCd":"/Saxvehmz4RPKZDKNMvSKQ==","Subtitle_CD":"nG6tVgEQPGU2GvOIdnwTjg==","SOUNDX_YN":"nG6tVgEQPGU2GvOIdnwTjg==","Third_Attr_CD":"nG6tVgEQPGU2GvOIdnwTjg==","Language":"zqWM417GS6dxQ7CIf65+iA=="}' --compressed 2>/dev/null
"""

theater_dict = {
    "왕십리 CGV" : "0074",
    "용산아이파크몰 CGV" :"0013",
    "gwang gyo CGV" :"0257"
}

movie_dict = {
    "어벤져스 : 엔드게임" : "20019245",
    "명탐정 피카츄" : "20019134"
}

class MovieInfo() :
    def __init__(self, info, params) :
        self.start_time = info[0]
        self.end_time = info[1]
        self.screen_name = info[2]
        self.params = params

def print_dict(data, depth) :
    if type(data) == list :
        for idx, item in enumerate(data) :
            print("   "*depth+"+-", "item %d" % idx)
            print_dict(item, depth+1)
    elif type(data) == dict :
        for key in data.keys() :
            print("   "*depth+"+-", key)
            print_dict(data[key], depth+1)
    else :
        print("   "*depth+"+-", data)


class CGVSeatInfo() :

  def __init__(self) :
    self.request_cmd_dict = dict()
    self.encrypt = CGV_AES().encrypt
    self.royal_seats = dict()
    self.reservation_info = dict()
    self.seat_str = dict()
    self.theater = ""
    self.movie = ""
    self._input_movie()
    self._input_theater()
    self.schedule = {}
    self._get_date_schedule()
    self.max_row = 0
    self.max_col = 0

  def encrypt_tuple(self, data) :
      t = tuple([self.encrypt(i) for i in data])
      return t

  def _input_theater(self) :
      print("select theater")
      for idx, theater in enumerate(theater_dict.keys()) :
          print("  %d : %s" % (idx+1, theater))
      idx = int(input("choose number : "))-1
      if idx in range(0, len(theater_dict.keys())) :
          self.theater = theater_dict[list(theater_dict.keys())[idx]]
      else :
          print("invailed input value")
          exit(-1)

  def _input_movie(self) :
      print("select movie")
      for idx, movie in enumerate(movie_dict.keys()) :
          print("  %d : %s" % (idx+1, movie))
      idx = int(input("choose number : "))-1
      if idx in range(0, len(movie_dict.keys())) :
          self.movie = movie_dict[list(movie_dict.keys())[idx]]
      else :
          print("invailed input value")
          exit(-1)

  def _get_date_schedule(self) :
    params = (self.theater, self.movie)
    req_cmd = date_table_cmd % self.encrypt_tuple(params)
    xml = self._get_xml_with_cmd(req_cmd)
    data = self._xml_to_dict(xml)["CSchedule"]["PlayDays"]["CPlayDay"]
    for dict_item in data :
        self.schedule[dict_item["PLAY_YMD"]] = {"FORMAT_DATE": dict_item["FORMAT_DATE"]}

    for i, date in enumerate(self.schedule.keys()) :
        params = (self.movie, self.theater, date)
        req_cmd = time_table_cmd % self.encrypt_tuple(params)
        xml = self._get_xml_with_cmd(req_cmd)
        data = self._xml_to_dict(xml)["NewDataSet"]["Table"]
        time_schedule = []
        for j, item in enumerate(data) :
            t=(i*len(data) + j+1)/((len(self.schedule.keys()))*(len(data)))
            print("\r예약 가능 날짜 검색하는중... ["+"#"*int(t*20)+"-"*(20-int(t*20))+("]%.2f %%" % (t*100)), end="")
            play_num = item["PLAY_NUM"]
            start_time = item["PLAY_START_TM"]
            end_time = item["PLAY_END_TM"]
            screen_code = item["SCREEN_CD"]
            screen_name = item["SCREEN_NM"]
            params = self.encrypt_tuple((self.theater, date, screen_code, play_num))
            info = (start_time, end_time, screen_name)
            time_schedule.append(MovieInfo(info, params))
        self.schedule[date]["TIME_TABLE"] = time_schedule
        time.sleep(0.5)
    print()
    for i in self.schedule.keys() :
        print(" ", self.schedule[i]["FORMAT_DATE"])
    if(input("위 날짜 크롤링 ㄱ? y/n ") != "y") :
        exit(-1)


  def update_seat_info(self) :
    for i, datetime in enumerate(self.schedule.keys()) :
      for j, movie in enumerate(self.schedule[datetime]["TIME_TABLE"]) :
        t=(i*len(self.schedule[datetime]["TIME_TABLE"]) + j+1)/((len(self.schedule.keys()))*len(self.schedule[datetime]["TIME_TABLE"]))
        print("\r존좋자리 검색중... ["+"#"*int(t*20)+"-"*(20-int(t*20))+("]%.2f %%" % (t*100)), end="")
        request_cmd = seat_info_cmd % movie.params
        seat_info_list = self.reservation_info[datetime] = self.get_seat_info_with_cmd(request_cmd)

        key = "%s %s %s ~ %s" % (movie.screen_name, self.schedule[datetime]["FORMAT_DATE"], movie.start_time, movie.end_time)
        self.royal_seats[key] = self.get_royal_seats(seat_info_list)
        self.seat_str[key] = self.get_seat_info_str(seat_info_list)
        time.sleep(0.5)
    print()

  def get_royal_seats(self, seat_info_list) :
    royal_seats = []

    if seat_info_list == None :
      return None
    for seat_item in seat_info_list :
      if seat_item[2] == "Y" and self.isFuckingAbsolutelySupurPowerfulDefinitlySuccessfulRoyalSeat(seat_item) :
        royal_seats.append(seat_item)

    return royal_seats

  def _get_xml_with_cmd(self, request_cmd) :
    req_str = subprocess.check_output(request_cmd, shell=True)
    raw_json_data = json.loads(req_str.decode("utf-8"))
    xml = raw_json_data["d"]["data"]["DATA"]
    return xml

  def _xml_to_dict(self, xml_str) :
    dict_to_ret = json.loads(json.dumps(xmltodict.parse(xml_str), indent=4))
    return dict_to_ret

  def get_seat_info_with_cmd(self, request_cmd) :
    xml_str = self._get_xml_with_cmd(request_cmd)
    new_data_set = self._xml_to_dict(xml_str)["NewDataSet"]
    if "SEAT_INFO" in new_data_set.keys() :
      seat_info_dict = new_data_set["SEAT_INFO"]
    else :
      return None
    seat_info_list = [(int(seat["LOC_X"]), int(seat["LOC_Y"]), seat["SEAT_STATE"]) for seat in seat_info_dict]
    self.find_max_row_col(seat_info_list)
    return seat_info_list

  def find_max_row_col(self, seat_list) :
    if self.max_col == 0 and self.max_row == 0 :
      for item in seat_list :
          if item[0] > self.max_col :
              self.max_col = item[0]
          if item[1] > self.max_row :
              self.max_row = item[1]

  def get_seat_info_str(self, seat_info_list) :
    if seat_info_list == None :
      return ""
    max_row = self.max_row
    max_col = self.max_col

    col_info = "".join(["%3d" % i for i in range(1, max_col+1)])
    row_info = " ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    seat_info = [["   " for i in range(max_col)] for j in range(max_row)]

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
    return self.max_col/4 < seat_info[0] < self.max_col/4*3 and self.max_row/2 < seat_info[1]

def main() :
  cgv_crawler = CGVSeatInfo()

  while(1) :
    cgv_crawler.printRoyalSeat()
    time.sleep(3)

main()
