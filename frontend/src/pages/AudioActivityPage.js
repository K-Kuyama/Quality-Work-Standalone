import React, { useState } from 'react';
import AudioActivityTable from "../components/AudioActivityTable";
import AudioControlPanel from "../components/AudioControlPanel";
import AudioSettings from "../components/AudioSettings";


/* アクティビティーリストページ */
function AudioActivityPage(){
    const [target_date, setDate] = useState(new Date());
    //const [item, setItem] = useState("event_list");


	//Controlパネルから、setDateとsetItemを個別に呼び出すように変更したので、setParams は現在は使っていない（後で消す？）
//    const setParams = (date_str, item_str) => {
//        setDate(date_str.target_date);
//   	console.log(target_date)
//        setItem(item_str.target_item);
//      console.log(item);        
//    }

	return(
        <div className="top_app">
            <AudioSettings />
            <div className="app_page">
                <div className="sidebar">
                    <div id="a-controls" className="controls">
                    <div className="a-cntpanel">
                        {/* <ControlPanel handler={setParams}/> */}		
                        <AudioControlPanel date_handler={setDate} />
                    </div>
                    </div>
                </div>
                <div className="contents">
                    <AudioActivityTable target_date={target_date} />  
                </div>
            </div>
        </div>
	)

}

export default AudioActivityPage;