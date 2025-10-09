//import React, { useState, useEffect } from 'react';
import Accordion from 'react-bootstrap/Accordion';
import Button from 'react-bootstrap/Button';
import Settings from "../Settings";

function RegisteredActivities(props){

	const setDefChange = props.handler;



	const deleteRActivities = (e) => {
		// アクティビティ削除用ハンドラー
		// チェックが入ったものをデータベースから削除。
		// 削除によるイベントセレクターの選択表示を変更するために、setDefChangeを呼ぶ
		
		let activities = document.querySelectorAll("input[name=registered_item]:checked")
		let request_body = []
		for (const act of activities){
			request_body.push(act.id);
			act.checked = false;
		}
		console.log("->", activities, activities.length);

		let target = Settings.HOME_PATH+"/api/user_def/delete_c_activity/"
		if(Settings.DEVELOP){
			target = Settings.DEVELOPMENT_HOME_PATH+"/api/user_def/delete_c_activity/"
		}

		if(activities.length > 0){
			fetch(target, {
				method : "POST",
				headers: {'Content-Type' : 'application/json',},
				body : JSON.stringify(request_body)		
				}
			)
			.then(result =>{
				setDefChange(true);
			})
			.catch(error =>{
				console.error(error);
			})
		}
	}

	const registered_act_pane= () =>{
		if(props.activities.length > 0){
			return(
				<div className="registered_act_pane">
					<div className="registered_act_box">
					{props.activities.map((a) =>{
						return (
						<div>
							<input name="registered_item" type="checkbox" id={a.id} style={{width: "24px"}} /> 
							<label for={a.id}> {a.app} : {a.title} </label>
						</div>
						);
					})}	
					</div>
					<div className="ra_tail">
						<Button variant="secondary" className="btn btn-dlt-ppheader" size="sm" onClick={(e)=> deleteRActivities(e)} > 削除 </Button>	
					</div>
				</div>
			)
		} else {
			return(
				<div className="editor-message-line">
					<label className="editor-message">アクティビティは登録されていません</label>
				</div>
			)			
		}
	}

	if(props.no_accordion){	
		return(
			<>
				{registered_act_pane()}
			</>
			)
	} else {
		return(
			<div className="activity_accordion">
				<Accordion className="registered-activities">
					<Accordion.Item eventKey="0">
						<Accordion.Header className="registered-activities-header" >登録済みアクティビティー</Accordion.Header>
						<Accordion.Body>
							{registered_act_pane()}
						</Accordion.Body>
					</Accordion.Item>
				</Accordion>
		</div>
		)
	}
	

}
export default RegisteredActivities;