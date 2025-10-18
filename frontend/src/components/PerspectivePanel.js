import React, { useState, useEffect } from 'react';
import Button from 'react-bootstrap/Button';
import Offcanvas from 'react-bootstrap/Offcanvas';
import SidebarDefEditor from './SidebarDefEditor';
import Settings from "../Settings";

function PerspectivePanel(props){

	const [data, setData]= useState([]);
	const [haveData, setHaveData] = useState(false); 
	const [menueChanged, setMenueChanged] = useState(false);
	const setParam = props.handler;
	const setChanged = props.set_check;
	
	const [show, setShow] = useState(false);
	const handleClose = () => setShow(false);
	const handleShow = () => setShow(true);


	const getInitialPid = (data) =>{
		let pid = 0;
		for(let p of data){
			if(p['categorize_model']!='InputValueModel'){
				pid = p['id'];
				break;
			}
		}
		return pid;
	} 
	

	/* propsに変更があった時に呼び出される */
	useEffect(() => {
		let target = Settings.HOME_PATH+'/api/user_def/Perspective/'
		if(Settings.DEVELOP){
			target = Settings.DEVELOPMENT_HOME_PATH+'/api/user_def/Perspective/'
		}			
		fetch(target,{
					credentials: "same-origin",
				}
		)
		.then(response => {
			return response.json();
		})
		.then(result =>{
			const txt = JSON.stringify(result, null,' ');
			let res = JSON.parse(txt);
			setData(res);
			if(!haveData){
				setParam(getInitialPid(res));
			}
			setHaveData(true);
			setChanged(false);
			setMenueChanged(false);
			
			//checkPid();
		})
		.catch(error =>{
			setHaveData(false);
			setChanged(false);
			setMenueChanged(false);
			console.error('----Error---');
			console.error(error);
		})
	
	},[props, menueChanged]);


	if (!haveData) {
		return <div>Loading...</div>
	} else{
		return(
			<>
				<div className="perspectives">	
					<div className="pp_header2">
						<Button type="button" className="btn btn-ppheader" data-bs-toggle="button" size="sm" value="edit" 	onClick={handleShow}>
    						編集
    					</Button>
					</div>
    				<div className="d-grid gap-2">
    					{data.map((obj) =>{
    						if(obj['categorize_model']=="InputValueModel"){
    							return(
    								<Button type="button" class="btn btn-light" data-bs-toggle="button" variant="light" size="sm" 
    									value={obj['id']} onClick={(e) => setParam(e.target.value)}>
    									{obj['name']}
    								</Button>
    							)
    						}
    					})}
    					
    					<hr size="5" color="white" ></hr>
    					{data.map((obj) =>{
    						if(obj['categorize_model'] != "InputValueModel"){
    							return(
    								<Button type="button" class="btn btn-light" data-bs-toggle="button" variant="light" size="sm" 
    									value={obj['id']} onClick={(e) => setParam(e.target.value)}>
    									{obj['name']}
    								</Button>
    							)
    						}
    					})}

    					
    				</div>
				</div>
				{/* 編集ボタンを押すと現れるオフキャンパス */}
				<Offcanvas show={show} onHide={handleClose}>
        			<Offcanvas.Header closeButton className="perspective-off-title">
          				<Offcanvas.Title >ビューの編集</Offcanvas.Title>
        			</Offcanvas.Header>
        			<Offcanvas.Body className="perspective-offcanvas">
          				<SidebarDefEditor data={data} handler={setMenueChanged}/>
        			</Offcanvas.Body>
      			</Offcanvas>
			</>
		);
	}


}

export default PerspectivePanel;