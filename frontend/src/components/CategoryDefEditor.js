import React, { useState } from 'react';
import Button from 'react-bootstrap/Button';
//import Accordion from 'react-bootstrap/Accordion';
import Cookies from "universal-cookie";
import Settings from "../Settings";

function CategoryDefEditor(props){

	//const [c_id, setCid] = useState(props.id);
	const [c_name, setName] = useState(props.name);
	const [c_color, setColor] = useState(props.color);
	//const [pid, setPerspective] = useState(props.pid)

	const handleText = (e) => setName(e.target.value);
	const handleColor = (e) => setColor(e.target.value);
	
	const handleChangeCategory = props.handler;
	
	const setCategoryInfo =()=>{
		console.log("perspective id -->",props.pid);
		if(props.id == '0'){
			setCategory(props.pid, c_name, c_color, true);
		}
		else{
			setCategory(props.pid, c_name, c_color, false);
		}	
	};

	const setCategory = (p_id, c_name, c_color,  c_new) => {
		let additional_str ="" ;
		let method_str = "POST";
		if(!c_new){
			additional_str =props.id+"/";
			method_str = "PATCH";
		}
		let request_body = {perspective: p_id, name: c_name, color: c_color};
		console.log(request_body);
		let cookies = new Cookies();
		let token = cookies.get('csrftoken')
		fetch(Settings.HOME_PATH+"/api/user_def/Category/"+additional_str, {
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
			//console.log("Category set result ", result);
			//console.log("res id=", result['id']);
			handleChangeCategory(result['id']);	
		})
		.catch(error =>{
			console.error(error);
		})
	}

/*
	const deleteCategory = (id) => {
		fetch("http://127.0.0.1:8000/api/user_def/Category/"+id+"/", {
			method : 'DELETE',
			headers: {'Content-Type' : 'application/json',}	
			}
		)
		.then(response => {
			handleChangeCategory(0);	
		})
		.catch(error =>{
			console.error(error);
		})

	
	}


	const setDeleteButton = ()=>{
		if(props.c_id == '0'){

			return(<></>);
		}
		else{
			return(
				<Button variant="primary" size="sm" style={{marginLeft: "20px"}} onClick={(e)=> deleteCategory(props.id)} > 削除 </Button>
			)
		}
	}
*/

	return(

        					<div className="perspective_def_body">
        						<div className="p_info_setter">
        							<div style={{width: "40px", color: "white"}}> 名称 </div>
        							<input type="text" id="perspective_name" style={{marginLeft: "10px", width: "160px"}} 
        								defaultValue={props.name} 
        								onChange={handleText} ></input>
        						</div> {/* p_info_setter */}
        						<div className="p_info_setter">
        							<div style={{width: "40px", color: "white"}}> 色 </div>
        								<input type="color" id="perspective_color" defaultValue={props.color}
        									onChange={handleColor} style={{marginLeft: "10px", width: "80px"}}></input>
        						</div> {/* p_info_setter */}
        						<div className="p_info_tail">
        							<Button variant="secondary" size="sm" style={{width: "50px", marginRight: "20px"}} onClick={(e)=> setCategoryInfo()}> 
        								保存 </Button>
        						</div>
        						{/* setDeleteButton() */}
        					</div>
	)


}

export default CategoryDefEditor;