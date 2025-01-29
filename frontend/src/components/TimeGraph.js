import React, { useState, useEffect } from 'react';
import { getBothEnds } from "./utils"
import Settings from "../Settings";

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from "chart.js";
import { Bar } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

// Chartjs用のグラフデータを作成する
function createGraphData(res, g_color){

	let labels = res.map((obj) => obj['index'])
	let data_list = res.map((obj) => obj['value'])
	//console.log("================")	
	//console.log(labels)
	//console.log(data_list)
	//console.log("================")	

	return {labels: labels, datasets:[{data:data_list, backgroundColor: g_color}],};
}

function TimeGraph(props){
	// props
	//  kind_of_value : 表示するデータの種類。duration, strokes, scrolls, distanceのいづれか
	//  kind_of_period : 表示する時間種別。year, month, week, dayのいづれか
	//  target_date : 表示する日付。時間種別がyear, month, weekの場合、この日付を含む時間が表示される
	

	//const [target_date, setDate] = useState(props.target_date);
	const [haveData, setHaveData] = useState(false); 
	const [g_data, setGData]=useState([]);
	
	var y_max = undefined;
	var y_stepSize = undefined;

	var title_text = undefined;
	let g_color = 'rgba(53, 162, 235, 0.5)'
	
	let td = new Date(props.target_date)	
	
	// 時間(duration)表示の場合、以下を設定する
	//  ticks_callback : Y軸に表示する時間
	//  y_stepSize : Y軸の単位
	//  y_max : Y軸の最大値
	//  title_text : グラフ上部に表示する日付
	//  g_color : グラフ色
	
	if(props.kind_of_value === "duration"){
		var ticks_callback = function(val){
			return val/3600+"時間"
		};
		if(props.kind_of_period === "year"){
			y_stepSize = 72000;
			title_text = td.getFullYear() + "年";
			g_color = 'rgba(255, 215, 50, 0.5)'
		}else if (props.kind_of_period === "month"){
			y_stepSize = 7200;
			title_text = td.getFullYear() + "年 "+ (td.getMonth()+1) + "月";
			g_color = 'rgba(50, 205, 50, 0.5)'
		}else if (props.kind_of_period === "week"){
			y_stepSize = 7200;
			td.setDate(td.getDate() - td.getDay());
			title_text = td.getFullYear() + "年 "+ (td.getMonth()+1) + "月 "+td.getDate()+"日 の週";
			g_color = 'rgba(232, 76, 108, 0.5)'
		}else{
			y_max = 3600;
			y_stepSize = 900;
			ticks_callback = function(val){
  						return val/60+"分"
  					};
			title_text = props.target_date;		
		}
	}
	
	// グラフに渡すオプション設定
	const options = {
  		responsive: true,
  		scales:{
 			
  			y:{				// OK
  				min: 0, 
  				max: y_max,
  				grid:{
  					color: "#666666",
  				},
  				ticks:{
  					min: 0,
  					max: y_max,      
  					stepSize: y_stepSize,	
  					callback: ticks_callback
  					}
  				}		
  			},

		//凡例、タイトル、ツールチップの設定
  		plugins: {
  			legend: {
        		// 凡例の非表示
        		display: false,
      		},
    		title: {
      			display: true,
      			text: title_text,	// OK
    		},
    		tooltip:{
	  			callbacks:{
	  				label: function(val){
	  						if(props.kind_of_value == "duration"){
								let s = val['raw']%60;
								let t = Math.floor(val['raw']/60)
								if(t < 1)
									return s+"秒"
								else{
									let m = t%60;
									t = Math.floor(t/60);
									if (t <1)
										return m+"分 "+s+"秒";
									else{
										let h = t;
										return h+"時間"+m+"分 "+s+"秒";
									}
								}
							}
							else {
								return val['raw'];
							}
  						}
  				}
  			}
		}
	}

	// propsが変更された時に、サーバからデータを取得し、グラフデータを作る
	useEffect(() => {
		//setDate(props.target_date);
		//console.log("debug : target_date = ", props.target_date);
		if(props.target_date){
			let date = new Date(props.target_date);
			let both_ends = getBothEnds(date, props.kind_of_period);		// OK
			let d1 = both_ends[0];
			let d2 = both_ends[1];
			let params = {start : d1, end : d2, kind_of_period : props.kind_of_period, kind_of_value : props.kind_of_value}		// OK
			let query = new URLSearchParams(params);

			fetch(Settings.HOME_PATH+'/api/Activity/total_event_time_for_periodical/?'+ query,{
						credentials: "same-origin",
					}
			)
			.then(response => {
				return response.json();
			})
			.then(result =>{
				const txt = JSON.stringify(result, null,' ');
				//console.log('---Success ---');
				//console.log(txt);
				let res = JSON.parse(txt);
				//取得したデータからグラフ用データを作成し、g_dataに格納
				let gd = createGraphData(res, g_color)
				setGData(gd);
				setHaveData(true);
			})
			.catch(error =>{
				setHaveData(false);
				console.error('----Error---');
				console.error(error);
			})
		}
	},[props]);

	if (!haveData) {
		return <div>Loading...</div>
	} else{
		return(
			<div className="hourly_graph">
				<Bar options={options} data={g_data} width='80%' height="12px" />
			</div>
		);
	}
}

export default TimeGraph;