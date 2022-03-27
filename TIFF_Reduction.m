% Brendan Luke
% March 26, 2022
% TIFF reduction
clear, clc, close all
format compact
tic
%% Load Image
imData = imread('LRO_LOLA_DEM_SPole75_30m.tif');

%% Process Image
% fix mirroring:
imData2 = imData(end:-1:1,:);
% reduce data:
reduce = 32; % factor to reduce data
n = length(imData2(:,1))/reduce; % number of data points (1D)
imData_reduce = zeros(n,'int16');
for i = 1:length(imData2(:,1))/reduce
    for j = 1:length(imData2(:,1))/reduce
        imData_reduce(i,j) = imData2(reduce*i,reduce*j);
    end
end

% dump full-res image data for memory purposes:
clearvars imData imData2

%% Plot
figure();
h = surf(imData_reduce);
set(h,'edgecolor','none');
b = 7; % number of bits for colour scale
yurt = zeros(2^b,3);
for i = 1:2^b
    yurt(i,:) = (i)/2^b;
end
colormap(yurt)
axis equal
ch = get(gca,'children');
set(gca,'visible','off') % turn axis off
ch.Clipping = 'off';    % turn clipping off
view([0,0,1]);

%% Create TIFF
t = Tiff('myfile.tif','w');

tagstruct.ImageLength = size(imData_reduce,1); 
tagstruct.ImageWidth = size(imData_reduce,2);
tagstruct.Photometric = Tiff.Photometric.MinIsBlack;
tagstruct.BitsPerSample = 16;
tagstruct.SamplesPerPixel = 1;
tagstruct.SampleFormat = Tiff.SampleFormat.Int;
tagstruct.PlanarConfiguration = Tiff.PlanarConfiguration.Chunky; 
tagstruct.Software = 'MATLAB'; 

setTag(t,tagstruct);

write(t,imData_reduce);
close(t);

%% Stop Clock
toc