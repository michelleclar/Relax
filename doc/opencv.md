# 本项目核心OpenCV

### 六种匹配模板

1. CV_TM_SQDIFF 平方差匹配法：计算图像像素间的距离之和，最好的匹配是0，值越大，是目标的概率就越低。
   $$
   $ R(x,y) = \Sigma_{x',y'}  (T(x',y) - I(x+x',y+y'))^2$
   $$
2. CV_TM_CCORR 相关匹配法：一种乘法操作；数值从小到大，匹配概率越来越高。
   $$
   $R(x,y) = \Sigma_{x',y'}  (T(x',y') \cdot I(x+x',y+y'))
   $$


3. CV_TM_CCOEFF 相关系数匹配法：从-1到1，匹配概率越来越高。
   $$
   R(x,y) = \Sigma_{x',y'}  (T'(x',y') \cdot I'(x+x',y+y')) \\
   \text{where} \\
   T'(x',y') = T(x',y') - 1/(w\cdot h)\cdot \Sigma_{x",y"}T(x'',y'') \\
   I'(x+x',y+y')) = I'(x+x',y+y') - 1/(w\cdot h)\cdot \Sigma_{x",y"}I(x+x'',y+y'')
   $$

4. CV_TM_SQDIFF_NORMED 归一化平方差匹配
   $$
   $R(x,y) = \frac{\Sigma_{x',y'} T(x',y) + I(x+x',y+y')}{\sqrt{\Sigma_{x',y'} T(x',y') \cdot \Sigma_{x',y'}I(
   x+x',y+y')}}
   $$

5. CV_TM_CCORR_NORMED 归一化相关匹配
   $$
   R(x,y) = \frac{\Sigma_{x',y'}  (T(x',y') \cdot I(x+x',y+y'))}{\sqrt{\Sigma_{x',y'} T(x',y')^2 \cdot \Sigma_{x',y'}I(
   x+x',y+y')^2}}
   $$

6. CV_TM_CCOEFF_NORMED 归一化相关系数匹配

$$
$R(x,y) = \frac{\Sigma_{x',y'}  (T'(x',y') \cdot I'(x+x',y+y'))}{\sqrt{\Sigma_{x',y'} T'(x',y')^2 \cdot \Sigma_{x',y'
}I'(x+x',y+y')^2}}
$$

