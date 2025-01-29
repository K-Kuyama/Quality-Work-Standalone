import React, { useState, useEffect } from 'react';
import { getBothEnds } from "./utils"

import {ArcElement, Chart as ChartJS, Legend, Tooltip} from 'chart.js'
import {Pie} from 'react-chartjs-2'
import Settings from "../Settings";

function createGraphData(res){

	let labels = res.map((obj) => obj['categoryName'])
	let data_list = res.map((obj) => obj['activities'][0]['duration'])
	let color_list = res.map((obj) => obj['backgroundColor'])
	
	let data = {
		labels: labels,
		datasets: [
			{ data: data_list, backgroundColor: color_list, borderColor: color_list, borderWidth: 1}
		]
	};
	
	
	//console.log(data);
	return data;
}



function CategoryGraph(props){

	//const [target_date, setDate] = useState(props.target_date);
	//const [p_id, setPid] = useState(props.p_id);
	const [haveData, setHaveData] = useState(false); 
	const [g_data, setGData]=useState([]);

	const options ={
		maintainAspectRatio: false,
	   	responsive: true,
		plugins:{
			tooltip:{
				callbacks: {
					label: function(context){
						let sum = context['dataset']['data'].reduce(function(a,b){return a+b;});
						let p_val = parseInt(context['raw']/sum *1000)/10;
						console.log(sum);
						console.log(p_val);

						let s = context['raw']%60;
						let t = Math.floor(context['raw']/60)
							if(t < 1)
								return s+"秒 : "+p_val+"%";
							else{
								let m = t%60;
								t = Math.floor(t/60);
								if (t <1)
									return m+"分 "+s+"秒 : "+p_val+"%";
								else{
									let h = t;
									return h+"時間"+m+"分 "+s+"秒 : "+p_val+"%";
								}
							}				
						
					}
				}
			}, // tooltip
			legend:{
				position: "right",
				maxWidth: 200,
			}
		},

	}


	
//	const getPerspective = (p_id) =>{
//		if(p_id != 0){
//			fetch('http://127.0.0.1:8000/api/user_def/_Perspective/'+ p_id +'/')
//			.then(response => {
//				return response.json();
//			})
//			.then(result =>{
//				const txt = JSON.stringify(result, null,' ');
//				console.log('---Success ---');
//				console.log(txt);
//				let res = JSON.parse(txt);
//			})
//			.catch(error =>{
//				console.error('----Error---');
//				console.error(error);
//			})
//		}		
//	}



	useEffect(() => {
		//setDate(props.target_date);
		if(props.target_date && props.p_id){
			let date = new Date(props.target_date);
			//console.log("date for graph:", date);
			//console.log("pid for graph:", props.p_id);
			let both_ends = getBothEnds(date, "day");		
			let d1 = both_ends[0];
			let d2 = both_ends[1];
			let params = {start : d1, end : d2, p_id: props.p_id, summarize: true }	
			let query = new URLSearchParams(params);
		
			// getPerspective(props.p_id);
			fetch(Settings.HOME_PATH+'/api/Activity/sort_out_by_categories/?'+ query,{
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
				let gd = createGraphData(res)
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

	ChartJS.register(ArcElement, Tooltip, Legend)
	if (!haveData) {
		return <div>Loading...</div>
	} else{
		if (props.no_title){
			return(
				<div className="inner_pie_graph">
						<Pie data={g_data} options={options}/>
				</div>
			);
		}
		else
		{
			return(
				<div className="pie_graph_pane">
					<div className="pie_graph_title">
						<h2>{props.p_name}</h2>
					</div>
					<div className="pie_graph">
						<Pie data={g_data} options={options}/>
					</div>
				</div>
			);
		}
	}



}

export default CategoryGraph;