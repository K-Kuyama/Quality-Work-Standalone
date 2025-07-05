import React, { useState, useEffect, useContext } from 'react';
import Button from 'react-bootstrap/Button';
import { ShowPolicyContext } from '../Context';
import {getOptions, createData} from './TimeChart';

//import { ja } from "date-fns/locale";
import Settings from "../Settings";

import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    TimeScale
    //TooltipPositionerMap,
    //ChartOptions
  } from "chart.js";
  
  import { Bar } from "react-chartjs-2";
  import "chartjs-adapter-date-fns";
  
  ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    //ChartDataLabels,
    TimeScale
  );


function TimeChartOption(props){
	//const [isVisible, setVisibility] = useState(false);
    
	//const [g_data, setData] = useState({});
	//const [g_options, setOptions] = useState({});
	//const [haveData, setHaveData] = useState(false);

    const [p_id, setPerspective] = useState(props.pid);
    const [range, setRange] = useState([]);
    const [g_data, setData] = useState(undefined);

    const ctx = useContext(ShowPolicyContext);

    const getRange = (fromTo) =>{
        console.log(fromTo);
        let from = new Date(fromTo[0]);
        let st_str = 
            from.getFullYear() + '-' + ('0' + (from.getMonth() + 1)).slice(-2) + '-' + ('0' + from.getDate()).slice(-2) + " " +
            ('0' + from.getHours()).slice(-2) + ":00:00.000000";
        let to = new Date(fromTo[1]);
        console.log(to);
        to.setHours(to.getHours() + 1);
        console.log(to);
        let end_str = 
            to.getFullYear() + '-' + ('0' + (to.getMonth() + 1)).slice(-2) + '-' + ('0' + to.getDate()).slice(-2) + " " +
            ('0' + to.getHours()).slice(-2) + ":00:00.000000";
        let duration = (new Date(end_str)).getTime() - (new Date(st_str)).getTime();
        return [st_str, end_str, duration];
    };

    const displayDetail = () =>{
        let range = getRange(props.from_to);
        //console.log("range",range);
        setRange(range);
        let policy = ctx.policy
        let params = {start : range[0], end : range[1], p_id : props.p_id, show_policy : policy};

        let query = new URLSearchParams(params);
        let target = Settings.HOME_PATH+'/api/Activity/working_time_chart/?'
        if(Settings.DEVELOP){
            target = Settings.DEVELOPMENT_HOME_PATH+'/api/Activity/working_time_chart/?'
        }
        fetch(target + query	
        )
        .then(response => {
            return response.json();
        })
        .then(result =>{
            const txt = JSON.stringify(result, null,' ');
            //console.log('---Success ---');
            //console.log(txt);
            let res = JSON.parse(txt);
            let dt = createData(res);
            //console.log(dt);
            //let dts = getData()
            //console.log(dts);
            let op = getOptions(dt, range[0], range[1], props.p_id, true);
            setData([dt,op]);

        })
        .catch(error =>{
            setData([]);
            console.error('----Error---');
            console.error(error);
        })
        //setRange(range);
        //setVisibility(true);
    }

    useEffect(() => {
        //console.log("g_data", g_data);
        //console.log("props.p_id",props.p_id);
        setPerspective(props.p_id);
    }, [props]);


	if(g_data){
		return(
                <div className="scrolled_graph_base">

                    <div className="scrollable_base">
                            <div  style={{height: "100px", width: String(range[2]/4000)+"px"}}>
                                <Bar options={g_data[1]} data={g_data[0]}  />
                            </div>
                    </div>
     
                    <div className="p_info_tail">
                        <Button variant="outline-light" size="sm" style={{margin: "6px", width: "80px"}} onClick={(e)=> setData(undefined)}> <i class="bi bi-x-lg"></i> 閉じる</Button>
                    </div> 
                    
                </div>
		)
	} else {
		return(
			<div className="p_info_tail">
				<Button type="button" className="btn btn-ppheader" data-bs-toggle="button" size="sm" style={{margin: "6px", width: "80px"}} onClick={(e)=> displayDetail()} >
    				詳細
    			</Button>
            </div>
    	
		)
	}



}

export default TimeChartOption;