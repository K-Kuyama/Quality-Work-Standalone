import React, { useState, useEffect } from 'react';
import { getBothEnds } from "./utils"

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

function createGraphData(res){

	let labels = res.map((obj) => obj['index'])
	let data_list = res.map((obj) => obj['duration'])
	console.log("================")	
	console.log(labels)
	console.log(data_list)
	console.log("================")	

	return {labels: labels, datasets:[{data:data_list, backgroundColor:'rgba(53, 162, 235, 0.5)'}],};
}

function HourlyGraph(props){

	const [target_date, setDate] = useState(props.target_date);
	const [haveData, setHaveData] = useState(false); 
//	const [data, setData]=useState([]);
	const [g_data, setGData]=useState([]);
	const options = {
  		responsive: true,
  		scales:{
 			
  			y:{
  				min: 0, 
  				max: 3600,
  				grid:{
  					color: "#666666",
  				},
  				ticks:{
  					min: 0,
  					max: 3600,
  					stepSize: 900,
  					callback: function(val){
  						return val/60+"分"
  					}
  				}		
  			},
  		},

  		plugins: {
  			legend: {
        		// 凡例の非表示
        		display: false,
      		},
    		title: {
      			display: true,
      			text: props.target_date,
    		},
    		tooltip:{
	  			callbacks:{
	  				label: function(val){
	  					let m = Math.floor(val['raw']/60)
	  					let s = val['raw']%60
	  					if (m > 0)
	  						return m+"分 "+s+"秒"
	  					else
	  						return s+"秒"
  				}
  			},
  		},
  		},
	};

	
	useEffect(() => {
		setDate(props.target_date);
		let date = new Date(props.target_date);
		let both_ends = getBothEnds(date);
		let d1 = both_ends[0];
		let d2 = both_ends[1];
		let params = {start : d1, end : d2, kind_of_period : "day"}
		let query = new URLSearchParams(params);
//		fetch('http://127.0.0.1:8000/api/Activity/total_event_time_by_hour/?'+ query)
		fetch('http://127.0.0.1:8000/api/Activity/total_event_time_for_periodical/?'+ query)
		.then(response => {
			return response.json();
		})
		.then(result =>{
			const txt = JSON.stringify(result, null,' ');
			console.log('---Success ---');
			console.log(txt);
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

export default HourlyGraph;