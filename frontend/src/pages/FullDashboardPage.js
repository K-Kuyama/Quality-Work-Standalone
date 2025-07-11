import React, { useState } from 'react';
import BarGraphsPanel from "../components/BarGraphsPanel";
import TimeChart from "../components/TimeChart";
import TopItems from '../components/TopItems';
import TimeGraph from "../components/TimeGraph";
import CategorizedTimeGraph from "../components/CategorizedTimeGraph";
import CategoryGraph from "../components/CategoryGraph"

function FullDashoboardPage(){
    const [target_date, setDate] = useState(new Date());
    const [p_id, setPid] = useState([]);
  

    return(
		<div className="app_page">
			<div className="sidebar">
				<div id="controls" className="controls">
				<div className="cntpanel">
					{/* <ControlPanel handler={setParams}/> */}		
					<BarGraphsPanel date_handler={setDate} pid_handler={setPid} />
				</div>
				</div>
			</div>
			<div className="contents">
                
                <div className="graph_base">
                <label className="graph_name">タイムチャート</label>
				    <TimeChart target_date={target_date} p_id={p_id[0]} />
                </div>


                <div className="graph_base">
				    <label className="graph_name">時系列グラフ</label>
                    <TimeGraph target_date={target_date} kind_of_period="day" kind_of_value="duration" />
                </div>
                
                
                <div className="graph_base">
				    	<label className="graph_name">時系列グラフ</label>
                        <CategorizedTimeGraph target_date={target_date} p_id={p_id} kind_of_period="day"/>
                </div>
                
                <div className="row_items_base">
                    <div className="inner_graph_base_l">
                        <label className="graph_name">トップタイトル</label>
                        <TopItems target_date={target_date} item="title" />
                    </div>
                    <div className="inner_graph_base_r">
                        <label className="graph_name">トップアプリ</label>
                        <TopItems target_date={target_date} item="app" />
                    </div>
                </div>
               
                <div className="row_items_base">
                    <div className="inner_graph_base_c">
                        <label className="graph_name">{p_id[1]}</label>
                        <CategoryGraph p_id={p_id[0]} p_name={p_id[1]} target_date={target_date} no_title="true" />
                    </div>
                </div>
               
			</div>
        </div>
	)
}

export default FullDashoboardPage;