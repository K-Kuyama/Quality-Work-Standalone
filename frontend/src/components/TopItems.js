import React, { useState, useEffect, useContext } from 'react';
import { getBothEnds } from "./utils";
import Settings from "../Settings";
import { ShowPolicyContext } from '../Context';

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
  
  function TopItems(props){

	const [data, setData]= useState([]);
	const [haveData, setHaveData] = useState(false); 	
	const ctx = useContext(ShowPolicyContext)

	let g_color = 'rgba(53, 162, 235, 0.5)'
	const item = props.item
	//if(props.item == "app"){
	//	g_color = 'rgba(232, 76, 108, 0.5)';
	//}
	
	// Chartjs用のグラフデータを作成する
	const createGraphData = (res, g_color) =>{
		let tl = res.slice(0,5);
		let labels = tl.map((obj) => createLabel(obj));
		let data_list = tl.map((obj) => obj['duration']);
		//console.log("================")	
		//console.log(labels)
		//console.log(data_list)
		//console.log("================")	
		return {labels: labels, datasets:[{data:data_list, backgroundColor: g_color}],};
	}

	const createLabel = (obj) =>{
		if(props.item === "app"){
				return obj['app'];
			} else{
				return obj['app']+":"+obj['title'];
			}
	}
	
	

	useEffect(() => {
		if(props.target_date){
			let date = new Date(props.target_date);
			let both_ends = getBothEnds(date);
			let d1 = both_ends[0];
			let d2 = both_ends[1];
			let policy = ctx.policy
			let params = {start : d1, end : d2, show_policy : policy, merged_item: item, sorted_by: 'duration'};
			let query = new URLSearchParams(params);

			let target = Settings.HOME_PATH+'/api/Activity/merged_event/?'
			if(Settings.DEVELOP){
				target = Settings.DEVELOPMENT_HOME_PATH+'/api/Activity/merged_event/?'
			}
			fetch(target + query,{
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
				let gd = createGraphData(res, g_color)
				setData(gd);
				setHaveData(true);
			})
			.catch(error =>{
				setHaveData(false);
				console.error('----Error---');
				console.error(error);
			})
		}
	},[props])

	const x_max = undefined;
	const x_stepSize = 1800;
	const ticks_callback = function(val){
			return val/3600+"時間"
		};
		
	// グラフに渡すオプション設定
	const options = {
		maintainAspectRatio: false,
	   	responsive: true,
		indexAxis: "y",
		scales:{	
  			x:{				// OK
  				min: 0, 
  				max: x_max,
  				grid:{
  					color: "#666666",
  				},
  				ticks:{
  					min: 0,
  					max: x_max,      
  					stepSize: x_stepSize,	
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
      			display: false,
      			text: "",	// OK
    		},
	    	tooltip:{
	  			callbacks:{
	  				label: function(val){
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
				}
			}
		}
	}
	
	if (!haveData) {
		return <div>Loading...</div>
	} else{
		return(
			<div className="top_item_graph">
				<Bar options={options} data={data} />
			</div>
		);
	}

}

export default TopItems;