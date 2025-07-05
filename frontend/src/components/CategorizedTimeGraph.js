import React, { useState, useEffect, useContext } from 'react';
import { getBothEnds } from "./utils"
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


function createLabelSets(clist){
	if (clist.length >0){
		return createLabels(clist[0]['data_array']);
	}
	else{
		return []
	}
}

function createLabels(dlist){
	let labels = [];
	dlist.map((d) => {
		labels.push(d['index'])
	});
	return labels;
}

function createData(dlist){
	let data = [];
	dlist.map((d) => {
		data.push(d['value'])
	});
	return data;
}

function createDataSets(clist){
	let datasets = [];
	clist.map((cdata) =>{
		//console.log(cdata);
		datasets.push({labels:cdata['name'], backgroundColor:cdata['backgroundColor'], data: createData(cdata['data_array'])})		
	})
	return datasets;
}

function createGraphData(res, g_color){

	let labels = createLabelSets(res);
	// let labels = createLabels(res[0]['data_array']);
	//console.log(labels);
	let datasets = createDataSets(res);
	//console.log("================");
	//console.log(datasets);
	//console.log("================");	

	return {labels: labels, datasets: datasets,};
}

function CategorizedTimeGraph(props){

	//const [target_date, setDate] = useState(props.target_date);
	const [haveData, setHaveData] = useState(false); 
	const [g_data, setGData]=useState([]);
	
	const ctx = useContext(ShowPolicyContext)

	var y_max = undefined;
	var y_stepSize = undefined;
	var ticks_callback = function(val){
			return val/3600+"時間"
		};
	var title_text = undefined;
	let g_color = 'rgba(53, 162, 235, 0.5)'
	
	let td = new Date(props.target_date)	
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
	
	
	const options = {
  		responsive: true,
  		scales:{
  			x:{
  					stacked: true
  			},
  			y:{				// OK
  					stacked: true,
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
	  				beforeLabel: function(val){
	  						return val.dataset.label;
	  					},
	  				label: function(val){
								let s = val['raw']%60;
								let t = Math.floor(val['raw']/60)
								if(t < 1)
									return [val.dataset.labels, s+"秒"];
								else{
									let m = t%60;
									t = Math.floor(t/60);
									if (t <1)
										return [val.dataset.labels, m+"分 "+s+"秒"];
									else{
										let h = t;
										return [val.dataset.labels, h+"時間"+m+"分 "+s+"秒"];
									}
								}
  							}
  				}
  			}
		}
	}

	
	useEffect(() => {
		//setDate(props.target_date);
		if(props.target_date && props.p_id[0]){
			let date = new Date(props.target_date);
			let both_ends = getBothEnds(date, props.kind_of_period);		// OK
			let d1 = both_ends[0];
			let d2 = both_ends[1];
			let policy = ctx.policy
			let params = {start : d1, end : d2, kind_of_period : props.kind_of_period, p_id: props.p_id[0], show_policy : policy}		// OK
			let query = new URLSearchParams(params);
			let target = Settings.HOME_PATH+'/api/Activity/periodical_categories/?';
			if(Settings.DEVELOP){
				target = Settings.DEVELOPMENT_HOME_PATH+'/api/Activity/periodical_categories/?'
			}
			fetch(target+ query, {
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
				//console.log(res);
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

export default CategorizedTimeGraph;