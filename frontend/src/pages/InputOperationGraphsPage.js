import React, { useState} from 'react';
import {formatDateJa} from "../components/utils";
import InputOperationPanel from "../components/InputOperationPanel";
//import CategorizedTimeGraph from "../components/CategorizedTimeGraph";
import TimeGraph from "../components/TimeGraph";

function InputOperationGraphsPage(props){

    const [target_date, setDate] = useState();
    //const [p_id, setPid] = useState(0)

	// 時間種別ごとにサイドバーの操作パネルに表示するタイトルを返す
	const getPanelTitle = (kind) =>{
		if(kind ==="day"){
			return "日次集計情報";
		}
		else if(kind ==="week"){
			return "週次集計情報";
		}
		else if(kind ==="month"){
			return "月次集計情報";
		}
		else if(kind ==="year"){
			return "年次集計情報";
		}
		else {
			return "";
		}
	}
	
	// コンテンツページに表示するタイトルを返す
	const getContentsTitle = (kind) =>{
		if(target_date){
			if(kind ==="day"){
				return formatDateJa(target_date);
			}
			else if(kind ==="week"){
				return target_date.getFullYear() + "年 "+ (target_date.getMonth()+1) + "月 "+target_date.getDate()+"日 の週";
			}
			else if(kind ==="month"){
				return target_date.getFullYear() + "年 "+ (target_date.getMonth()+1) + "月";
			}
			else if(kind ==="year"){
				return target_date.getFullYear() + "年";
			}
			else {
				return "";
			}
		}
		else return"";
	}
	

	// ログ表示のためのダミー
	// 日付変更の際に表示される
	//useEffect(() =>{
    //	console.log("target_date :: ", target_date);
    //},[target_date])
	

	return(
		<div className="app_page">
			<div className="sidebar">
				<div id="controls" className="controls_wide">
					<label className="graph_panel_title">{getPanelTitle(props.kind_of_period)}</label>
					<InputOperationPanel date_handler={setDate} kind_of_period={props.kind_of_period} />
				</div>
			</div>
			<div className="contents">
				<label className="graph_contents_title">{getContentsTitle(props.kind_of_period)}</label>
				<div className="graph_base">
						<label className="graph_name">時間</label>
                        <TimeGraph target_date={target_date} kind_of_period={props.kind_of_period} kind_of_value="duration"/>
                </div>
 				<div className="graph_base">
 						<label className="graph_name">キー入力数</label>
                        <TimeGraph target_date={target_date} kind_of_period={props.kind_of_period} kind_of_value="strokes"/>
                </div>
  				<div className="graph_base">
  						<label className="graph_name">スクロール回数</label>
                        <TimeGraph target_date={target_date} kind_of_period={props.kind_of_period} kind_of_value="scrolls"/>
                </div>
                <div className="graph_base">
                		<label className="graph_name">マウスドラッグ距離</label>
                        <TimeGraph target_date={target_date} kind_of_period={props.kind_of_period} kind_of_value="distance"/>
                </div>
			</div>
		</div>
	)


}

export default InputOperationGraphsPage;