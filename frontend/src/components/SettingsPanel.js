import React, { useState, useEffect } from 'react';

function SettingsPanel(props){
    const categories =[['audio','オーディオ設定'], ['db_settings','データベース設定'],]


    const [target_item, setItem] = useState("audio");
    const setCategory = props.handler;

    // このコンポーネントと親ページの両方のアイテムを設定
	// radioボタンの値の変更(onChange)で呼び出される
	const setTargetItem = (d) =>{
		//let sd = getBothEnds(d, props.kind_of_period);
		//console.log('set item -->', d);
		let item = d.target.value;
		setCategory(item);		
		setItem(item);
	};


	return(
		<>	

			<div className="item_panel">
				<label className="date_title" key="item_title-1">設定種別</label>
				<div className="c_select">
					{categories.map((condition) => {
						return (
							<label><input type="radio" name="items" id={"id-"+condition[0]} value={condition[0]} checked={condition[0] === target_item} onChange={setTargetItem} />
						 	&nbsp;{condition[1]} </label>
						)
					})}	
				</div>
			</div>
						
		</>
	);


}

export default SettingsPanel;