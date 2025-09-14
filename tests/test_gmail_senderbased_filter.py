import unittest
from unittest.mock import MagicMock, patch
from src import Gmail_SenderBased_Filter as gsf

class TestGmailSenderBasedFilter(unittest.TestCase):
    def setUp(self):
        self.mock_service = MagicMock()

    def test_get_or_create_label_existing(self):
        self.mock_service.users().labels().list().execute.return_value = {
            'labels': [{'id': '123', 'name': 'TestLabel'}]
        }
        label_id = gsf.get_or_create_label(self.mock_service, 'TestLabel')
        self.assertEqual(label_id, '123')

    def test_get_or_create_label_new(self):
        self.mock_service.users().labels().list().execute.return_value = {
            'labels': []
        }
        self.mock_service.users().labels().create().execute.return_value = {'id': '456'}
        label_id = gsf.get_or_create_label(self.mock_service, 'NewLabel')
        self.assertEqual(label_id, '456')

    def test_list_all_messages(self):
        mock_list = self.mock_service.users().messages().list
        mock_list.return_value.execute.side_effect = [
            {'messages': [{'id': '1'}, {'id': '2'}]},
            {'messages': [{'id': '3'}]}
        ]
        self.mock_service.users().messages().list_next.side_effect = [
            self.mock_service.users().messages().list.return_value,
            None
        ]
        result = gsf.list_all_messages(self.mock_service, 'query')
        self.assertEqual(result, ['1', '2', '3'])

    @patch('src.Gmail_SenderBased_Filter.tqdm', lambda x, **kwargs: x)
    def test_filter_unlabeled_messages_bulk(self):
        self.mock_service.users().messages().get().execute.side_effect = [
            {'labelIds': ['INBOX']},
            {'labelIds': ['INBOX', 'LBL1']},
            {'labelIds': ['LBL2']}
        ]
        message_ids = ['a', 'b', 'c']
        label_id = 'LBL1'
        result = gsf.filter_unlabeled_messages_bulk(self.mock_service, message_ids, label_id)
        self.assertEqual(result, ['a', 'c'])

    @patch('src.Gmail_SenderBased_Filter.tqdm', lambda x, **kwargs: x)
    def test_process_messages_in_batches(self):
        message_ids = ['1', '2', '3', '4']
        label_id = 'LBL1'
        # Patch tqdm.write to avoid printing
        with patch('src.Gmail_SenderBased_Filter.tqdm.write'):
            gsf.process_messages_in_batches(self.mock_service, message_ids, label_id, batch_size=2)
        # Should call batchModify twice
        self.assertEqual(self.mock_service.users().messages().batchModify.call_count, 2)

if __name__ == '__main__':
    unittest.main()
