import { useState } from 'react';

function AboutThisPanel(props){
    const docs =[['AboutQW.txt','このソフトウェアについて'], ['AboutLicense.txt','ソフトウェアライセンス'],
                ['JS_LICENSES.txt','Third-party Libraries (JavaScript)'],
                ['PY_LICENSES.txt','Third-party Libraries (Python)'],]


    const [target_item, setItem] = useState('AboutQW.txt');
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
                <label className="date_title" key="item_title-1">文書</label>
                <div className="c_select">
                    {docs.map((doc) => {
                        return (
                            <label><input type="radio" name="items" id={"id-"+doc[0]} value={doc[0]} checked={doc[0] === target_item} onChange={setTargetItem} />
                            &nbsp;{doc[1]} </label>
                        )
                    })}	
                </div>
            </div>
                        
        </>
    );


}

export default AboutThisPanel;