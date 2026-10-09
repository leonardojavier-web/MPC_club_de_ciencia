import { useEffect, useState } from 'react';
import { getFoundation } from '../services/api';

export function useFoundationData({ loadFoundation = getFoundation } = {}) {
  const [data, setData] = useState([]);
  const [connected, setConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let active = true;

    loadFoundation()
      .then((records) => {
        if (active) {
          setData(records);
          setConnected(true);
        }
      })
      .catch((error) => {
        console.error('Error al obtener los datos de fundación', error);
        if (active) setConnected(false);
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });

    return () => {
      active = false;
    };
  }, [loadFoundation]);

  return { data, connected, isLoading };
}