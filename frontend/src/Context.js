import React, { useState, createContext, useCallback} from 'react'

//audioアクティビティを表示するポリシーを保持するためのContext
export const ShowPolicyContext = createContext();

export function useShowPolicy() {
    const [policy, setPolicy] = useState(0);
    const updatePolicy = useCallback((policy) => {setPolicy(policy)},[]);  
    
    return({policy, updatePolicy});

}



