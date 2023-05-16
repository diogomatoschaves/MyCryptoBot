import React, { useState, useEffect } from 'react';

const withWindowSizeListener = (Component: any) => {
  return function (props: any) {
    const [windowWidth, setWindowWidth] = useState(window.innerWidth);

    useEffect(() => {
      const handleResize = () => {
        setWindowWidth(window.innerWidth);
      };

      window.addEventListener('resize', handleResize);

      // Clean up the event listener when the component is unmounted
      return () => {
        window.removeEventListener('resize', handleResize);
      };
    }, [])

    const size = windowWidth > 1919
      ? "large"
      : windowWidth > 992
        ? "desktop"
        : windowWidth > 768
          ? "tablet"
          : "mobile"

    return <Component size={size} {...props}/>;
  };
}

export default withWindowSizeListener;
