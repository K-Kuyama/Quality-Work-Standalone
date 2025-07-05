import React, { useState, useEffect, useContext } from 'react';
import { getBothEnds } from "./utils"
import { ShowPolicyContext } from '../Context';
import {ArcElement, Chart as ChartJS, Legend, Tooltip} from 'chart.js'
import {Doughnut, Pie} from 'react-chartjs-2'
import Settings from "../Settings";

function createGraphData(res){
	let border_color = "#575977"
	let p_labels = [];
	let p_data_list = [];
	let p_color_list = [];
	let p_border_list = [];
	let s_labels = [];
	let s_data_list = [];
	let s_color_list = [];
	let s_border_list = [];
	for (let p_category of res){
		let duration = 0;
		for (let s_category of p_category['categories']){
			let dr = parseInt(s_category['activities'][0]['duration']);
			duration += dr;
			s_data_list.push(dr);
			s_labels.push(s_category['categoryName']);
			s_color_list.push(s_category['backgroundColor']);
			s_border_list.push(border_color)
		}
		p_data_list.push(duration);
		p_labels.push(p_category['categoryName']);
		p_color_list.push(p_category['backgroundColor']);
		p_border_list.push(border_color)
	}

	let p_data ={
		labels: p_labels,
		datasets: [
			{ data: p_data_list, backgroundColor: p_color_list, borderColor: p_border_list, borderWidth: 1}			
		]
	};	
	let s_data ={
		labels: s_labels,
		datasets: [
			{ data: s_data_list, backgroundColor: s_color_list, borderColor: s_border_list, borderWidth: 1}			
		]
	};
	//console.log(s_data);
	return ([p_data, s_data]);
}



function MultiCategoryGraph(props){

	const [haveData, setHaveData] = useState(false); 
	const [g_data, setGData]=useState([]);
	const ctx = useContext(ShowPolicyContext)

	const options ={
		plugins:{
			tooltip:{
				position: "average",
				callbacks: {
					label: function(context){
						let sum = context['dataset']['data'].reduce(function(a,b){return a+b;});
						let p_val = parseInt(context['raw']/sum *1000)/10;
						//console.log(sum);
						//console.log(p_val);

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
				display: false,
				position: "right",
				maxWidth: 200,
			}
		},
		maintainAspectRatio: false
	}




	useEffect(() =>{
		//console.log("target_date : ", props.target_date);
		//console.log("p_id : ", props.p_id);
		//console.log("sub_p_id : ", props.sub_p_id);
		if(props.target_date){
			let both_ends = getBothEnds(props.target_date, "day");		
			let d1 = both_ends[0];
			let d2 = both_ends[1];
			let policy = ctx.policy
			let params = {start : d1, end : d2, show_policy : policy, p_id: props.p_id[0], sub_p_id:props.sub_p_id[0], summarize: true }	
			let query = new URLSearchParams(params);
			let target = Settings.HOME_PATH+'/api/Activity/sort_out_by_multi_categories/?'
			if(Settings.DEVELOP){
				target = Settings.DEVELOPMENT_HOME_PATH+'/api/Activity/sort_out_by_multi_categories/?'
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
	},[props])



	ChartJS.register(ArcElement, Tooltip, Legend)
	if (!haveData) {
		return <div>Loading...</div>
	} else{
		return(
			<div className="pie_graph_pane">
				<div className="pie_graph_title">
					<label>{props.p_id[1]}</label> &nbsp;&&nbsp;
					<label>{props.sub_p_id[1]}</label>					
				</div>
				<div className="pie_relative">
					<Doughnut data={g_data[1]} options={options}/>
					<div className="pie_container">
						<Pie data={g_data[0]} options={options}/>
					</div>
				</div>
			</div>
		);
	}


}

export default MultiCategoryGraph;