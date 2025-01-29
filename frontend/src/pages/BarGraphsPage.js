import React, { useState } from 'react';
import BarGraphsPanel from "../components/BarGraphsPanel";
import CategorizedTimeGraph from "../components/CategorizedTimeGraph";

function BarGraphsPage(){

    const [target_date, setDate] = useState();
    const [p_id, setPid] = useState(0)

//    const setParams = (date_str, item_str) => {
//        setDate(date_str.target_date);
//   	console.log(target_date)
//        setItem(item_str.target_item);
//      console.log(item);        
//    }


	return(
		<div className="app_page">
			<div className="sidebar">
					<div className="controls">
						<BarGraphsPanel date_handler={setDate} pid_handler={setPid} />
					</div>
			</div>
			<div className="contents">
					<label className="graph_contents_title">カテゴリー別アクティブ時間グラフ</label>
				    <div className="graph_base">
				    	<label className="graph_name">日</label>
                        <CategorizedTimeGraph target_date={target_date} p_id={p_id} kind_of_period="day"/>
                    </div>
                    <div className="graph_base">
                    	<label className="graph_name">週</label>
                        <CategorizedTimeGraph target_date={target_date} p_id={p_id} kind_of_period="week"/>
                    </div>				
                    <div className="graph_base">
                    	<label className="graph_name">月</label>
                        <CategorizedTimeGraph target_date={target_date} p_id={p_id} kind_of_period="month"/>
                    </div>
                    <div className="graph_base">
                    	<label className="graph_name">年</label>
                        <CategorizedTimeGraph target_date={target_date} p_id={p_id} kind_of_period="year"/>
                    </div>          
			</div>
		</div>
	)


}

export default BarGraphsPage;