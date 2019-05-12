//reservation.step2.js

/*
parameter form :
  Language: "kor"
  PlayNum: "6"
  PlayYMD: "20190515"
  REQSITE: "CJSYSTEMS"
  ScreenCd: "009"
  TheaterCd: "0074"
*/
function loadSeatInfo(i) {
    var n = APILoader.init();
    n.URL = "/CJ000.aspx/CJ_002_PRIME_ZONE_LANGUAGE",
    n.PARAMS.Language = $.cgv.config.LANGUAGE,
    n.PARAMS.TheaterCd = $.cgv.data.고객선택정보.극장.극장코드,
    n.PARAMS.PlayYMD = $.cgv.data.고객선택정보.날짜.상영일자,
    n.PARAMS.ScreenCd = $.cgv.data.고객선택정보.상영관시간.상영관코드,
    n.PARAMS.PlayNum = $.cgv.data.고객선택정보.상영관시간.상영회차,
    $.cgv.net.loadAPI(n, n.PARAMS, {
        success: function(e) {
            var t = n.parseData(e);
            ft_ticket_prices = {},
            $(t.PRICE_INFO).each(function() {
                ft_ticket_prices[this.RATING_CD + this.TICKET_TYPE] = parseInt(this.PRICE, 10)
            });
            var a = t.SCREEN_INFO;
            $.cgv.data.고객선택정보.극장.극장명 = a.THEATER_NM,
            $.cgv.data.고객선택정보.극장.극장코드 = a.THEATER_CD,
            $.cgv.data.고객선택정보.상영관시간.상영관명 = a.SCREEN_NM,
            $.cgv.data.고객선택정보.상영관시간.상영관코드 = a.SCREEN_CD;
            var s = $("#user-select-info");
            s.find(".site").text(a.THEATER_NM),
            s.find(".screen").text(a.SCREEN_NM),
            $.cgv.data.SEAT_INFO = t,
            i()
        },
        error: silentLoadErrorListener
    })
}
