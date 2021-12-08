from pylab import *

def timeSeries(sperm, id, showGrid=False):

    T = sperm.getNumberOfGlyphs()
    time = arange(0,T)

    rows = 5; cols = 3

    subplot(rows,cols,1)
    plot(time, sperm.getVCLs(), 'bo', time, sperm.getVCLs(), 'k--', markerfacecolor='green')
    grid(showGrid)
    ylabel('VCL')

    subplot(rows,cols,2)
    plot(time, sperm.getVAPs(), 'bo', time, sperm.getVAPs(), 'k--', markerfacecolor='green')
    title('Sperm %d' % id)
    ylabel('VAP')

    subplot(rows,cols,3)
    plot(time, sperm.getVSLs(), 'bo', time, sperm.getVSLs(), 'k--', markerfacecolor='green')
    ylabel('VSL')

    subplot(rows,cols,4)
    plot(time, sperm.getWOBs(), 'bo', time, sperm.getWOBs(), 'k--', markerfacecolor='green')
    grid(showGrid)
    ylabel('WOB')

    subplot(rows,cols,5)
    plot(time, sperm.getLINs(), 'bo', time, sperm.getLINs(), 'k--', markerfacecolor='green')
    ylabel('LIN')

    subplot(rows,cols,6)
    plot(time, sperm.getSTRs(), 'bo', time, sperm.getSTRs(), 'k--', markerfacecolor='green')
    ylabel('STR')

    subplot(rows,cols,7)
    plot(time, sperm.getBCFs(), 'bo', time, sperm.getBCFs(), 'k--', markerfacecolor='green')
    ylabel('BCF')

    subplot(rows,cols,8)
    plot(time, sperm.getALHs(), 'bo', time, sperm.getALHs(), 'k--', markerfacecolor='green')
    ylabel('ALH')

    subplot(rows,cols,9)
    plot(time, sperm.getMADs(), 'bo', time, sperm.getMADs(), 'k--', markerfacecolor='green')
    ylabel('MAD')

    subplot(rows,cols,10)
    plot(time, sperm.getHeadLengths(), 'bo', time, sperm.getHeadLengths(), 'k--', markerfacecolor='green')
    ylabel('Head Lengths')

    subplot(rows,cols,11)
    plot(time, sperm.getHeadWidths(), 'bo', time, sperm.getHeadWidths(), 'k--', markerfacecolor='green')
    ylabel('Head Widths')

    subplot(rows,cols,12)
    plot(time, sperm.getHeadAngles(), 'bo', time, sperm.getHeadAngles(), 'k--', markerfacecolor='green')
    ylabel('Head Angles')

    subplot(rows,cols,13)
    plot(time, sperm.getAsymmetries(True), 'bo', time, sperm.getAsymmetries(True), 'k--', markerfacecolor='green')
    ylabel('Norm Asymmetry')
    xlabel('Beat Cycles T')

    subplot(rows,cols,14)
    plot(time, sperm.getTorques(True), 'bo', time, sperm.getTorques(True), 'k--', markerfacecolor='green')
    ylabel('Norm Torque')
    xlabel('Beat Cycles T')

    subplot(rows,cols,15)
    plot(time, sperm.getChangesInAngles(), 'bo', time, sperm.getChangesInAngles(), 'k--', markerfacecolor='green')
    ylabel('Change in Angles')
    xlabel('Beat Cycles T')

    show()
# end def

def timeSeriesAll(sperm, id, showGrid=False):

    T = sperm.getNumberOfGlyphs()
    time = arange(0,T)

    figure(1)
    plot( time, sperm.getVCLs(), 'r-o', markerfacecolor='red', label='VCL' )
    plot( time, sperm.getVAPs(), 'g-o', markerfacecolor='green',   label='VAP' )
    plot( time, sperm.getVSLs(), 'b-o', markerfacecolor='blue',  label='VSL' )

    plot(time, sperm.getWOBs(), 'r--s', markerfacecolor='red', label='WOB')
    plot(time, sperm.getLINs(), 'g--s', markerfacecolor='green',   label='LIN')
    plot(time, sperm.getSTRs(), 'b--s', markerfacecolor='blue',  label='STR')

    plot(time, sperm.getBCFs(), 'r-.^', markerfacecolor='red',    label='BCF')
    plot(time, sperm.getALHs(), 'g-.^', markerfacecolor='green', label='ALH')
    plot(time, sperm.getMADs(), 'b-.^', markerfacecolor='blue',  label='MAD')

    ylabel('value')
    xlabel('Beat Cycles T')
    grid(showGrid)
    legend()
    title('Time Series Data for a Single Sperm Cell')

    show()
# end def


