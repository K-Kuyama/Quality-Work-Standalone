import React, { useState } from 'react';
import ActivityTable from "../components/ActivityTable";
import ControlPanel from "../components/ControlPanel";

/* アクティビティーリストページ */
function ActivityListPage(){
    const [target_date, setDate] = useState(new Date());
    const [item, setItem] = useState("event_list");


	//Controlパネルから、setDateとsetItemを個別に呼び出すように変更したので、setParams は現在は使っていない（後で消す？）
//    const setParams = (date_str, item_str) => {
//        setDate(date_str.target_date);
//   	console.log(target_date)
//        setItem(item_str.target_item);
//      console.log(item);        
//    }

	return(
		<div className="app_page">
			<div className="sidebar">
				<div id="controls" className="controls">
				<div className="cntpanel">
					{/* <ControlPanel handler={setParams}/> */}		
					<ControlPanel date_handler={setDate} item_handler={setItem}/>
				</div>
				</div>
			</div>
			<div className="contents">
				<ActivityTable target_date={target_date} item={item} />  
			</div>
		</div>
	)

}

export default ActivityListPage;