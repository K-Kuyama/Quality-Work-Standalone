import React, { useState, useEffect } from 'react';
import DBStat from "./DBStat";
import Settings from "../Settings";

function DBInfoPanel(props){

	const titles =['ファイル', 'アップロード日時', 'データ数', '先頭', '最終','ステータス'];

	const [dbi, setDBInfo] = useState(null);
	const [upli, setULInfo] = useState([]);
	const [tableChanged, setTableChanged] = useState(false);
	const [haveData, setHaveData] = useState(false);
	const setChanged = props.setChanged;
	
	
	useEffect(() => {
		{/*
		let target = Settings.HOME_PATH+'/api/Activity/activity_db_info/1/'
		if(Settings.DEVELOP){
			target = Settings.DEVELOPMENT_HOME_PATH+'/api/Activity/activity_db_info/1/'
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
			//console.log('---Success ---');
			//console.log(txt);
			let res = JSON.parse(txt);
			setDBInfo(res);
			
		})
		.catch(error =>{
			console.error('----Error---');
			console.error(error);
		})
		*/}

		let target = Settings.HOME_PATH+'/api/Activity/file_upload/'
		if(Settings.DEVELOP){
			target = Settings.DEVELOPMENT_HOME_PATH+'/api/Activity/file_upload/'
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
			//console.log('---Success ---');
			//console.log(txt);
			let res = JSON.parse(txt);
			setULInfo(res);
			setHaveData(true);
		})
		.catch(error =>{
			console.error('----Error---');
			console.error(error);
		})
		
		setChanged(false);
				
	},[props, tableChanged]);
	
	if(haveData){
	return(
		<div className="db_info_panel">
			<div className="table_info_panel">
				<DBStat table="activity" />
				<DBStat table="audio" />
			</div>
			{/*
			<div className="db_status">
				<label>アクティビティーデータ情報</label>
					<table className="db_table">
						<tr><td>先頭データ</td><td>{dbi['startTime']}</td></tr>
						<tr><td>最終データ</td><td>{dbi['endTime']}</td></tr>
						<tr><td>データ数</td><td>{dbi['count']}</td></tr>
					</table>
			</div>
			*/}
			<div className="upload_info">
				<label>ファイルアップロード情報</label>
				<table className="db_table">
					<tr>
						{titles.map((title) => {
							return <th>{title}</th>;
						})}
					</tr>
					{upli.map((ui) =>{
						return(
							<tr>
								<td> {ui['fileName']}</td>
								<td> {ui['uploadTime']}</td>
								<td> {ui['dataCount']}</td>
								<td> {ui['startTime']}</td>
								<td> {ui['endTime']}</td>
								<td> {ui['status']}</td>
							</tr>
						)
					})}
				
				</table>
			</div>
		</div>
	)
}

}

export default DBInfoPanel;