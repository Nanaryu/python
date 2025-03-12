using System;
using System.Linq;
using System.Windows;

namespace WpfApp2
{
    public partial class MainWindow : Window
    {
        int step = 0;
        string[] answers = { "Answer 3", "Answer 1", "Answer 4", "Answer 2", "Answer 5" };
        string[] randans;

        public MainWindow()
        {
            InitializeComponent();
            randomans();
        }

        private void Window_Closing(object sender, System.ComponentModel.CancelEventArgs e)
        {
            if (step < answers.Length)
            {
                e.Cancel = true;
                letroll();
            }
        }

        private void letroll()
        {
            string question = $"Step {step + 1}: Is '{randans[step]}' the correct answer?";
            MessageBoxResult result = MessageBox.Show(question, "Le Troll", MessageBoxButton.YesNo, MessageBoxImage.Question);

            if ((result == MessageBoxResult.Yes && randans[step] == answers[step]) || (result == MessageBoxResult.No && randans[step] != answers[step]))
            {
                step++;
                if (step == answers.Length)
                {
                    MessageBox.Show("Congratulations!", "Yay", MessageBoxButton.OK, MessageBoxImage.Information);
                    Application.Current.Shutdown();
                }
            }
            else
            {
                MessageBox.Show("Wrong answer! Restarting sequence...", "Oof", MessageBoxButton.OK, MessageBoxImage.Warning);
                step = 0;
                randomans();
            }
        }

        private void randomans()
        {
            Random rng = new Random();
            randans = answers.OrderBy(x => rng.Next()).ToArray();
        }
    }
}
