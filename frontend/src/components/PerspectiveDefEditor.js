import React, { useState, useEffect } from 'react';
import Button from 'react-bootstrap/Button';
import Accordion from 'react-bootstrap/Accordion';
import Cookies from "universal-cookie";
import Settings from "../Settings";

function PerspectiveDefEditor(props){
	
	const [p_id, setPid] = useState(props.p_id);
	const [p_name, setName] = useState(props.name);
	const [p_color, setColor] = useState(props.color);
	const [use_def_color, setFlag] = useState(false);
	
	const handleText = (e) => setName(e.target.value);
	const handleColor = (e) => {setColor(e.target.value);
								console.log("set color : ", e.target.value);
								};
	
	const handleChangePerspective =	props.handler;

		
	const setPerspectiveInfo =()=>{
		if(props.p_id == '0'){
			setPerspective(p_name, p_color, use_def_color, true);
		}
		else{
			setPerspective(p_name, p_color, use_def_color, false);
		}
		
	};
	
	const setPerspective = (p_name, p_color, p_use_def_color, p_new) => {
		let additional_str ="" ;
		let method_str = "POST";
		if(!p_new){
			additional_str =props.p_id+"/";
			method_str = "PATCH";
		}
		let request_body ={name: p_name, color: p_color, use_def_color: p_use_def_color};
		let cookies = new Cookies();
		let token = cookies.get('csrftoken')
		fetch(Settings.HOME_PATH+"/api/user_def/Perspective/"+additional_str, {
			method : method_str,
			credentials: "same-origin",
			headers: {
					'Content-Type' : 'application/json',
					'X-CSRFToken': token,
				},
			body : JSON.stringify(request_body)		
			}
		)
		.then(response => response.json())
		.then(result =>{
			//console.log("perspective set original response ", result);
			const txt = JSON.stringify(result, null,' ');
			//console.log("perspective set text result ", txt);
			let res = JSON.parse(txt);
			//console.log("perspective set result ", res);
			//console.log("res id=", res['id']);
			handleChangePerspective(res['id']);	
		})
		.catch(error =>{
			console.error(error);
		})
	}
		
	const deletePerspective = (id) => {
		let cookies = new Cookies();
		let token = cookies.get('csrftoken')
		fetch("/api/user_def/Perspective/"+id+"/", {
			method : 'DELETE',
			credentials: "same-origin",
			headers: {
					'Content-Type' : 'application/json',
					'X-CSRFToken': token,
				}	
			}
		)
		.then(response => {
			handleChangePerspective(0);	
		})
		.catch(error =>{
			console.error(error);
		})

	
	}
	
		
	const setDeleteButton = ()=>{
		if(props.p_id == '0'){
			/* 新規設定の場合は削除ボタンは表示しない  */
			return(<></>);
		}
		else{
			return(
				<Button variant="primary" size="sm" style={{marginLeft: "20px"}} onClick={(e)=> deletePerspective(props.p_id)} > 削除 </Button>
			)
		}
	}
	
	
	return(
		<div className="perspective_accordion">
			<Accordion>
				<Accordion.Item eventKey="0">
    					<Accordion.Header>{props.name}</Accordion.Header>
        				<Accordion.Body>
        					<div className="perspective_def_body">
        						<div className="p_info_setter">
        							<div style={{width: "50px"}}> 名称 </div>
        							<input type="text" id="perspective_name" style={{marginLeft: "10px", width: "160px"}} 
        								placeholder={props.name} 
        								onChange={handleText} ></input>
        							<div style={{width: "50px"}}> 色 </div>
        								<input type="color" id="perspective_color" placeholder={props.color}
        									onChange={handleColor} style={{marginLeft: "10px", width: "80px"}}></input>
        							<Button variant="outline-secondary" size="sm" style={{marginLeft: "20px"}} onClick={(e)=> setPerspectiveInfo()}> 保存 </Button>
        						</div> {/* p_info_setter */}
        						{setDeleteButton()}
        					</div>
        				</Accordion.Body>
				</Accordion.Item>
			
			</Accordion>
		</div>
	)
	
	

}

export default PerspectiveDefEditor;