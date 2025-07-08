import { useCallback , useMemo, useState, useEffect} from 'react';
import { useDropzone } from 'react-dropzone';
import Button from 'react-bootstrap/Button';
import Cookies from "universal-cookie";
import Settings from "../Settings";
import {RouletteSpinnerOverlay} from "react-spinner-overlay";

const baseStyle = {
    display: "flex",
    flexDirection: "row",
    justifyContent: "space-between",
    width: "40%",
    height: 60,
};
const borderNormalStyle = {
    border: "2px dotted #888",
    backgroundColor: "rgba(255, 255, 255, 0.95)"
};
const borderDragStyle = {
    border: "3px solid #00f",
    transition: 'border .5s ease-in-out',
    backgroundColor: "rgba(255, 255, 255, 0.45)"
};




function DBLoader(props) {
    const [isVisible, setVisibility] = useState(false);
    const [db_info, setDBInfo] = useState([]);   //ソース側ファイルの内容
    const [result_info, setResult] =useState([]);  //テーブルのmigration結果
    const [target_file, setFile] = useState([]);  //選択されたソースDBファイル
    const [db_file_path, setDBPath] = useState(null); //アップロードされたソースDBファイルのパス
    const [f_id, setFId] = useState(null); //アップロードされたファイルエントリーのID
    const [query_list, setQueryList] = useState([]); //migrateするテーブルのリスト情報
    const [processing, setProcessing] = useState(false); //スピナーの表示状態
    
    const onDrop = useCallback((acceptedFiles) => {
        // Do something with the files
        //console.log('acceptedFiles:', acceptedFiles);
        let file = acceptedFiles[0];
        uploadFile(file);
        setFile(file);
    }, []);
    
    const { getRootProps, getInputProps, isDragActive, open, acceptedFiles } = useDropzone({
        onDrop,
        noClick: true
    });
    
    const style = useMemo(() => (
        { ...baseStyle, ...(isDragActive ? borderDragStyle : borderNormalStyle)}
    ), [isDragActive]);
    
    const setInitialState = (dbinfo) =>{
        let len = dbinfo.length;
        let state_list = new Array(len);
        state_list.fill("未反映");
        setResult(state_list);
    }

    const setDependency = (d) =>{
        if (d.target.checked){
            let dpn = d.target.getAttribute('data-parents');
            console.log(dpn);
            if(dpn){
                let plist = dpn.split('-');
                console.log(plist);
                for (const dp of plist){
                    console.log(dp);
                    let p = document.querySelector("#i"+dp);
                    p.checked = true;
                }
            }
        } 
        else {
            let dpn = d.target.getAttribute('data-children');
             if(dpn){
                let clist = dpn.split('-');
                console.log(clist);
                for (const dc of clist){
                    console.log(dc);
                    let p = document.querySelector("#i"+dc);
                    p.checked = false;
                }
            }
        }

    }

    const uploadFile = (file) =>{
        const formData = new FormData();
        const n_date = new Date();
    	formData.append('fileName', file.path);
    	formData.append('uploadTime', n_date.toISOString());
    	formData.append('contents', file);
        formData.append('status', "未反映");

        //let file_path ="";
        let cookies = new Cookies();
        let token = cookies.get('csrftoken');
        let target = Settings.HOME_PATH+'/system/dbupload/';
        if(Settings.DEVELOP){
            target = Settings.DEVELOPMENT_HOME_PATH+'/system/dbupload/'
        }
        fetch(target, {
            method : 'POST',
            credentials: "same-origin",
            headers: {
                    'X-CSRFToken': token,
                },
            body : formData,
            }
        )
        .then(response => {
			return response.json();
		})
        .then(result =>{
            const txt = JSON.stringify(result, null,' ');
            let res = JSON.parse(txt);
            setDBPath(res['path']);
            setFId(res['f_id']);
        })
        .catch(error =>{		
            console.error(error);
        })
        
    }


    const getDBInfo = (target_file) =>{
        //console.log("getDBInfo", target_file);
        let params = {file: target_file};
        let query = new URLSearchParams(params);
        let target = Settings.HOME_PATH+'/system/dbinfo/?'
        if(Settings.DEVELOP){
            target = Settings.DEVELOPMENT_HOME_PATH+'/system/dbinfo/?'
        }
        fetch(target+query,{
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
            setInitialState(res);
            setVisibility(true);
        })
        .catch(error =>{
            console.error('----Error---');
            console.error(error);
        })
    }


    const cancelFile = (e) =>{
        //アップロードしたファイルと関連する情報を消去する
        //console.log("cancelFIle",db_file_path, f_id);
        let params = {f_path: db_file_path};
        let query = new URLSearchParams(params);
        let cookies = new Cookies();
        let token = cookies.get('csrftoken')
        let target = Settings.HOME_PATH+'/system/UpdateHistory/'
        if(Settings.DEVELOP){
            target = Settings.DEVELOPMENT_HOME_PATH+'/system/UpdateHistory/'
        }
        if(f_id != null){
            fetch(target+f_id+"/?"+query,
                {
                    method: "DELETE",
                    credentials: "same-origin",
                    headers: {
                        'Content-Type' : 'application/json',
                        'X-CSRFToken': token,
                    },
                }
            )
            .then(response => {
                setVisibility(false);
                setDBPath(null);
                setDBInfo([])
                setFId(null);
            })
            .catch(error =>{
                console.error('----Error---');
                console.error(error);
            })
        }
    }


    const clearFile = () =>{
        // アップロードしたファイル情報を全てクリアする
        let cookies = new Cookies();
        let token = cookies.get('csrftoken')
        let target = Settings.HOME_PATH+'/system/history_clear/'
        if(Settings.DEVELOP){
            target = Settings.DEVELOPMENT_HOME_PATH+'/system/history_clear/'
        }
        fetch(target,
            {
                credentials: "same-origin",
                headers: {
                    'Content-Type' : 'application/json',
                    'X-CSRFToken': token,
                },
            }
        )
        .then(response => {
            setVisibility(false);
            setDBPath(null);
            setDBInfo([])
            setFId(null);
        })
        .catch(error =>{
            console.error('----Error---');
            console.error(error);
        })
        
    }

    const migrateData = (e) =>{
        let ilist = document.querySelectorAll("input[name=db_table]:checked")
        let qlist = [];
        for (let item of ilist){
            let tid = "#replace-"+item['id'].slice(1);
            let idx = Number(item['id'].slice(1));
            let replace = document.querySelector(tid).checked;
            //console.log(item["value"]);
            //console.log(replace);
            qlist.push({"table":item["value"], "replace": replace, "idx": idx})
        } 
        console.log("q_list:",qlist);
        setQueryList(qlist);
        setProcessing(true); //スピナーを表示する
    }

    const migrateTable = (name, replace, index) =>{
        let params = {file: db_file_path, table: name, replace: replace};
        console.log("migrateTable:",params)
        let query = new URLSearchParams(params);
        let target = Settings.HOME_PATH+'/system/tbmigrate/?'
        if(Settings.DEVELOP){
            target = Settings.DEVELOPMENT_HOME_PATH+'/system/tbmigrate/?'
        }
        fetch(target+query,{
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
            let r_info = Array.from(result_info);
            r_info[index] = res['result'];
            console.log("r_info:",r_info);
            setResult(r_info);

            let q_list = Array.from(query_list);
            q_list.shift();
            console.log("q_list:",q_list);
            setQueryList(q_list);
        })
        .catch(error =>{
            console.error('----Error---');
            console.error(error);
            let r_info = Array.from(result_info);
            r_info[index] = "Request error";
            setResult(r_info);

            let q_list = Array.from(query_list);
            q_list.shift();
            console.log("q_list:",q_list);
            setQueryList(q_list);
        })

    }


    useEffect(() =>{
        // uploadFile()によってDBファイルがアップロードされた後、そのファイルパスを
        // 指定してDBファイルの内容に関する情報を取得する
        if(db_file_path != null){
            getDBInfo(db_file_path);
        }
    },[db_file_path])

    useEffect(() =>{
        if (query_list.length > 0){
            let item = query_list[0];
            migrateTable(item["table"], item["replace"], item["idx"]);
        } else {
            setProcessing(false); //スピナーの表示を消す
        }
    },[query_list])

    useEffect(()=>{
        clearFile();
        return()=>{
            clearFile();
        }
    },[])

    return (
    	<div className="file_drop_area">
        	<div  {...getRootProps({ style })} >
         		<input {...getInputProps()} />
            		{
               	 isDragActive ?
                    <p>Drop the files here ...</p> :
                    <p>移行元のデータベースファイルをここにドラッグ＆ドロップするか、右のフォルダからファイルを選択</p>
            		}
        		 <Button variant="secondary" onClick={open}><i class="bi-folder2"></i></Button>
        	</div>
        	{isVisible ?
 			<div className="info_board">
 				<div className="file_contents_info">
 					<label>ファイル名: {target_file.path} </label>
                    <table>
                        <th>　</th><th>テーブル</th><th>行数</th><th>置換え</th><th>ステート</th>
                        {db_info.map((obj,ix) => {
                            return (<tr>
                                <td width="24px"><input type="checkbox" name="db_table" 
                                    data-parents={obj['parents']} data-children={obj['children']} 
                                    value={obj['name']} id={"i"+ix} onChange={setDependency} defaultChecked={true}/> </td> 
                                <td width="240pt"> <label for={ix}> {obj['name']}  </label> </td>
                                <td width="100pt"> <label for={ix}> {obj['count']} 行 </label> </td>
                                <td width="60px"><input type="checkbox" name="db_replace" value={obj['name']}
                                    id={"replace-"+ix} defaultChecked={obj['replace']} /> </td>
                                <td width="240pt"> <label for={ix} id={"state-"+ix}> {result_info[ix]} </label> </td>
                            </tr>
                            )
                        })}
                    </table>                    
 				</div>
    			<Button variant="primary" className="upload_b" onClick={(e)=> migrateData(e)} ><i class="bi-upload" ></i>アップロード</Button>
    			<Button variant="secondary" className="cancel_b" onClick={(e)=> cancelFile(e)} ><i class="bi-arrow-left-square"></i>閉じる</Button>
                <RouletteSpinnerOverlay loading={processing} overlayColor="rgba(0,153,255,0.2)" message="データ移行中" />
    		</div>
    		: <></>}
        </div>
        )


}

export default DBLoader;