import React, { useState } from 'react';
import AllGraphControlPanel from "../components/AllGraphControlPanel";
import TimeGraph from "../components/TimeGraph";

function AllGraphsPage(){

    const [target_date, setDate] = useState(new Date());
    //const [item, setItem] = useState("event_list");

//    const setParams = (date_str, item_str) => {
//        setDate(date_str.target_date);
//   	console.log(target_date)
//        setItem(item_str.target_item);
//      console.log(item);        
//   }

	return(
		<div className="app_page">
			<div className="sidebar">
				<div id="controls" className="controls">
					<AllGraphControlPanel date_handler={setDate} />
				</div>
			</div>
			<div className="contents">
					<label className="graph_contents_title">アクティブ時間グラフ</label>
				    <div className="graph_base">
				    	<label className="graph_name">日</label>
                        <TimeGraph target_date={target_date} kind_of_period="day" kind_of_value="duration" />
                    </div>
                    <div className="graph_base">
                    	<label className="graph_name">週</label>
                        <TimeGraph target_date={target_date} kind_of_period="week" kind_of_value="duration" />
                    </div>				
                    <div className="graph_base">
                    	<label className="graph_name">月</label>
                        <TimeGraph target_date={target_date} kind_of_period="month" kind_of_value="duration" />
                    </div>
                    <div className="graph_base">
                    	<label className="graph_name">年</label>
                        <TimeGraph target_date={target_date} kind_of_period="year" kind_of_value="duration" />
                    </div>          
			</div>
		</div>
	)


}

export default AllGraphsPage;