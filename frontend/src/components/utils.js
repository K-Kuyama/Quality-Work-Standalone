
export function getBothEnds(d, kind_of_period="day"){
/*
　入力された日付に対し、その日の開始時間と終了時間の配列を返す。
*/
	var date = new Date(d);

	if (kind_of_period === "year"){
		var d1 = date.getFullYear() + "-01-01 00:00:00.000";
		date.setFullYear(date.getFullYear() +1);
		var d2 = date.getFullYear() + "-01-01 00:00:00.000";
		return [d1, d2];
	} else if (kind_of_period === "month"){
		var d1 = date.getFullYear() + '-' + ('0' + (date.getMonth() + 1)).slice(-2) + "-01 00:00:00.000";
		date.setMonth(date.getMonth() +1);
		var d2 = date.getFullYear() + '-' + ('0' + (date.getMonth() + 1)).slice(-2) + "-01 00:00:00.000";
		return [d1, d2];
	} else if (kind_of_period === "week"){
		date.setDate(date.getDate() - date.getDay());
		var d1 = date.getFullYear() + '-' + ('0' + (date.getMonth() + 1)).slice(-2) + '-' +('0' + date.getDate()).slice(-2) + " 00:00:00.000";
		date.setDate(date.getDate() +7);
		var d2 = date.getFullYear() + '-' + ('0' + (date.getMonth() + 1)).slice(-2) + '-' +('0' + date.getDate()).slice(-2) + " 00:00:00.000";
		return [d1, d2];
	} else{
		var d1 = date.getFullYear() + '-' + ('0' + (date.getMonth() + 1)).slice(-2) + '-' +('0' + date.getDate()).slice(-2) + " 00:00:00.000";
		date.setDate(date.getDate() +1);
		var d2 = date.getFullYear() + '-' + ('0' + (date.getMonth() + 1)).slice(-2) + '-' +('0' + date.getDate()).slice(-2) + " 00:00:00.000";
		return [d1, d2];
	}
}

export function formatDate(date) {
  const year = date.getFullYear();
  const month = (date.getMonth() + 1).toString().padStart(2, '0');
  const day = date.getDate().toString().padStart(2, '0');
  return `${year}-${month}-${day}`;
}

export function formatDateJa(date){
  const year = date.getFullYear();
  const month = (date.getMonth() + 1).toString().padStart(2, '0');
  const dat = date.getDate().toString().padStart(2, '0');
  const day = date.getDay();
  const weekDay: {
  	[key: number]: string;
	} = {
  	0: '日曜日',
  	1: '月曜日',
  	2: '火曜日',
  	3: '水曜日',
  	4: '木曜日',
  	5: '金曜日',
  	6: '土曜日',
	};

  return `${year}年 ${month}月 ${dat}日 (${weekDay[day]})`;
}

// 日付の比較
// date1 lower than date2 の場合Trueを返す
export function lowerThanDateOnly(date1, date2) {
        var year1 = date1.getFullYear();
        var month1 = date1.getMonth() + 1;
        var day1 = date1.getDate();

        var year2 = date2.getFullYear();
        var month2= date2.getMonth() + 1;
        var day2 = date2.getDate();

        if (year1 == year2) {
            if (month1 == month2) {
                return day1 < day2;
            }
            else {
                return month1 < month2;
            }
        } else {
            return year1 < year2;
        }
    }

